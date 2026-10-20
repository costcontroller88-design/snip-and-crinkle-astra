"""Lossless per-shot drawing cache and one continuous final audio encode.

Opt-in API: render(shots, draw, dependencies, cache, size); encode(result, wav, out).
draw(shot, absolute_drawing_index) must be deterministic from the declared shot,
seed and dependencies. No hidden mutable state or undeclared files. Existing
episode renderers are unchanged; see docs/SELECTIVE_RENDERING.md for adoption.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave

import numpy as np
from PIL import Image, __version__ as PIL_VERSION

DPS, FPS = 15, 30


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dependency_hashes(paths):
    if not paths:
        raise ValueError("declare drawing code and asset dependencies")
    paths = {Path(p).resolve() for p in paths} | {Path(__file__).resolve()}
    return {str(p): digest(p) for p in sorted(paths)}


def validate(shots, size):
    if (not isinstance(size, (tuple, list)) or len(size) != 2 or
            any(type(x) is not int or x <= 0 or x % 2 for x in size)):
        raise ValueError("size must contain two positive even integers")
    if not isinstance(shots, list) or not shots:
        raise ValueError("provide at least one shot")
    end, ids = 0, set()
    for shot in shots:
        if not isinstance(shot, dict):
            raise ValueError("each shot must be an object")
        ident = shot.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-zA-Z0-9_-]+", ident) or ident in ids:
            raise ValueError("shot IDs must be unique neutral identifiers")
        ids.add(ident)
        if type(shot.get("start")) is not int or shot["start"] != end:
            raise ValueError("shots must cover consecutive drawing indices from zero")
        if type(shot.get("frames")) is not int or shot["frames"] <= 0:
            raise ValueError("shot frames must be a positive integer")
        if type(shot.get("seed")) is not int or not isinstance(shot.get("config"), dict):
            raise ValueError("each shot needs an integer seed and explicit config")
        json.dumps(shot, sort_keys=True, allow_nan=False)
        end += shot["frames"]
    return end


def valid_cache(folder, key, frames, size):
    try:
        if folder.is_symlink():
            return False
        receipt = json.loads((folder / "receipt.json").read_text())
        hashes = receipt["frame_sha256"]
        if receipt["key"] != key or len(hashes) != frames or receipt["size"] != list(size):
            return False
        for i, expected in enumerate(hashes):
            path = folder / f"d{i:05d}.png"
            if path.is_symlink() or digest(path) != expected:
                return False
            with Image.open(path) as image:
                if image.size != tuple(size) or image.mode != "RGB" or image.format != "PNG":
                    return False
                image.verify()
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def render(shots, draw, dependencies, cache, size=(1920, 1080)):
    """Cache complete shots atomically; return ordered frame paths and measured reuse.

    This serial renderer deliberately favors verified correctness over worker
    scaling. Only one writer may use a cache at a time; a lock fails fast.
    """
    # Freeze caller input so mutating a spec during drawing cannot alter the key.
    shots = json.loads(json.dumps(shots, allow_nan=False))
    count = validate(shots, size)
    dependencies = list(dependencies)
    stamp = dependency_hashes(dependencies)
    cache = Path(cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    lock = cache / ".writer.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    started, paths, frame_hashes, stats = time.perf_counter(), [], [], []
    try:
        for shot in shots:
            recipe = {"version": 1, "shot": shot, "dependencies": stamp, "size": list(size),
                      "dps": DPS, "fps": FPS, "pillow": PIL_VERSION, "numpy": np.__version__,
                      "python": sys.version}
            key = hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()
            folder = cache / key
            tick = time.perf_counter()
            hit = valid_cache(folder, key, shot["frames"], size)
            if not hit:
                if folder.is_symlink():
                    raise ValueError("cache entry must not be a symlink")
                temp = Path(tempfile.mkdtemp(prefix=".shot-", dir=cache))
                try:
                    hashes = []
                    for local in range(shot["frames"]):
                        # A private copy keeps a callback from modifying the keyed recipe.
                        frame = draw(json.loads(json.dumps(shot)), shot["start"] + local)
                        if not isinstance(frame, Image.Image) or frame.size != tuple(size):
                            raise ValueError("renderer returned the wrong image size/type")
                        path = temp / f"d{local:05d}.png"
                        clean = Image.frombytes("RGB", frame.size, frame.convert("RGB").tobytes())
                        clean.save(path)
                        hashes.append(digest(path))
                    if dependency_hashes(dependencies) != stamp:
                        raise ValueError("dependencies changed during rendering")
                    (temp / "receipt.json").write_text(json.dumps(
                        {"key": key, "recipe": recipe, "size": list(size), "frame_sha256": hashes}, indent=2))
                    if folder.exists():
                        shutil.rmtree(folder)  # Only the derived, corrupt hash entry is replaced.
                    os.rename(temp, folder)
                finally:
                    if temp.exists():
                        shutil.rmtree(temp)
            paths.extend(str(folder / f"d{i:05d}.png") for i in range(shot["frames"]))
            frame_hashes.extend(json.loads((folder / "receipt.json").read_text())["frame_sha256"])
            stats.append({"id": shot["id"], "key": key, "cache_hit": hit,
                          "drawings": 0 if hit else shot["frames"], "seconds": time.perf_counter() - tick})
        if dependency_hashes(dependencies) != stamp:
            raise ValueError("dependencies changed during rendering")
    finally:
        lock.unlink()
    return {"frames": paths, "frame_sha256": frame_hashes, "size": list(size), "drawings": count, "duration": count / DPS,
            "rendered_drawings": sum(s["drawings"] for s in stats), "shots": stats,
            "seconds": time.perf_counter() - started}


def encode(result, wav, output):
    """Always remux/re-encode continuous final audio; do not cache per-shot sound.

    Keeps the existing acting renderer's 15-drawing/30-frame cadence and encode
    settings. Final MP4 checks remain mandatory. Never publishes a failed encode.
    """
    output = Path(output)
    if output.exists():
        raise ValueError("output exists; use a new revision filename")
    if (len(result["frames"]) != result["drawings"] or
            len(result["frame_sha256"]) != result["drawings"] or
            result["duration"] != result["drawings"] / DPS):
        raise ValueError("inconsistent render result")
    with wave.open(str(wav), "rb") as audio:
        if audio.getnframes() / audio.getframerate() + 1e-9 < result["duration"]:
            raise ValueError("audio is shorter than the visual timeline")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".encode-", suffix=".mp4", dir=output.parent)
    os.close(fd)
    temp = Path(name)
    w, h = result["size"]
    command = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-i", str(wav),
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
               "-t", str(result["duration"]), "-movflags", "+faststart", str(temp)]
    try:
        with tempfile.TemporaryFile() as errors:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
            try:
                for path, expected in zip(result["frames"], result["frame_sha256"]):
                    if digest(path) != expected:
                        raise ValueError("cached frame changed before encode")
                    with Image.open(path) as image:
                        raw = image.convert("RGB").tobytes()
                        if image.size != (w, h):
                            raise ValueError("cached frame size changed before encode")
                    for _ in range(FPS // DPS):
                        proc.stdin.write(raw)
                proc.stdin.close()
                code = proc.wait()
                if code:
                    errors.seek(0)
                    raise RuntimeError("ffmpeg failed: " + errors.read().decode(errors="replace")[-2000:])
            finally:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                if not proc.stdin.closed:
                    try:
                        proc.stdin.close()
                    except BrokenPipeError:
                        pass
            os.rename(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    return str(output)
