"""Build and verify neutral storyboard sheets with declared moment coverage.

    python3 tools/storyboard_check.py BUNDLE --requirements moments.json --source table.md

Generation is exposed by stage.py covered-sheet. A PASS proves file integrity and
declared time coverage only. Meaning, clarity and safety require independent review.
The requirements and receipt are private to the builder; share only storyboard.png.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile

from PIL import Image, ImageDraw, ImageOps

REQUIRED = {"problem", "cause", "lesson", "payoff"}
MAX_PANELS = 48


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def coverage(requirements, times, duration):
    """Raise ValueError for invalid declarations or a missing time-window sample."""
    if not number(duration) or duration <= 0:
        raise ValueError("duration must be finite and positive")
    if not isinstance(times, list) or not 1 <= len(times) <= MAX_PANELS:
        raise ValueError(f"supply 1–{MAX_PANELS} panel times")
    if any(not number(t) or not 0 <= t < duration for t in times):
        raise ValueError("panel times must be finite and within [0, duration)")
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("panel times must be strictly increasing")
    if not isinstance(requirements, dict) or requirements.get("version") != 1:
        raise ValueError("requirements version must be 1")
    moments = requirements.get("moments")
    if not isinstance(moments, list) or not moments:
        raise ValueError("moments must be a nonempty list")
    ids, hits = set(), {}
    for moment in moments:
        if not isinstance(moment, dict):
            raise ValueError("each moment must be an object")
        name, start, end = (moment.get(k) for k in ("id", "start", "end"))
        if not isinstance(name, str) or not name.strip() or name in ids:
            raise ValueError("moment IDs must be nonempty and unique")
        ids.add(name)
        if not number(start) or not number(end) or not 0 <= start <= end < duration:
            raise ValueError(f"invalid moment window: {name}")
        hits[name] = [i + 1 for i, t in enumerate(times) if start <= t <= end]
        if not hits[name]:
            raise ValueError(f"missing panel for moment: {name} ({start:g}–{end:g})")
    missing = REQUIRED - ids
    if missing:
        raise ValueError("missing required moments: " + ", ".join(sorted(missing)))
    return hits


def compose(images, times):
    """Chronological panels, with only panel numbers and timestamps as labels."""
    portrait = images[0].height > images[0].width
    w, h = (270, 480) if portrait else (480, 270)
    cols = min(3, len(images))
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 12) + 12, rows * (h + 32) + 12), (250, 248, 242))
    draw = ImageDraw.Draw(sheet)
    for i, (im, t) in enumerate(zip(images, times)):
        x, y = 12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 32)
        # Contain, never crop or stretch a panel to make it fit.
        thumb = ImageOps.contain(im, (w, h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x + (w - thumb.width) // 2, y + (h - thumb.height) // 2))
        draw.text((x, y + h + 5), f"{i + 1}   {t:g}", fill=(60, 50, 50))
    return sheet


def write_bundle(render_frame, times, duration, requirements_path, source_path, output):
    """Render exact samples, then publish a fresh directory only after verification.

    render_frame is the source renderer, not a set of manually labelled images.
    Paths and hashes bind the table and moment file; renderer code is not certified.
    """
    requirements_path, source_path, output = map(Path, (requirements_path, source_path, output))
    requirements = json.loads(requirements_path.read_text())
    hits = coverage(requirements, times, duration)
    bindings = {"requirements_sha256": digest(requirements_path), "source_sha256": digest(source_path)}
    if output.exists():
        raise ValueError("output already exists; use a new revision directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".storyboard-", dir=output.parent))
    try:
        images, panels = [], []
        for i, t in enumerate(times, 1):
            frame = render_frame(t)
            if not isinstance(frame, Image.Image):
                raise ValueError("renderer must return a Pillow image")
            # Copy pixels into a fresh image; do not propagate source metadata.
            image = Image.frombytes("RGB", frame.size, frame.convert("RGB").tobytes())
            path = temp / f"panel_{i:03d}.png"
            image.save(path)
            images.append(image)
            panels.append({"time": t, "file": path.name, "size": list(image.size), "sha256": digest(path)})
        compose(images, times).save(temp / "storyboard.png")
        receipt = {"version": 1, "duration": duration, **bindings, "panels": panels,
                   "coverage": hits, "sheet_sha256": digest(temp / "storyboard.png")}
        (temp / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        verify(temp, requirements_path, source_path)
        os.rename(temp, output)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return output / "storyboard.png"


def verify(bundle, requirements_path, source_path):
    """Fail for stale inputs, corrupt panels, altered sheet, or missing coverage."""
    bundle = Path(bundle)
    receipt = json.loads((bundle / "receipt.json").read_text())
    if not isinstance(receipt, dict) or receipt.get("version") != 1:
        raise ValueError("receipt version must be 1")
    for key, path in (("requirements_sha256", requirements_path), ("source_sha256", source_path)):
        if receipt.get(key) != digest(path):
            raise ValueError(f"stale or changed input: {key}")
    panels = receipt.get("panels")
    if not isinstance(panels, list) or not all(isinstance(p, dict) for p in panels):
        raise ValueError("invalid panels list")
    times = [p.get("time") for p in panels]
    hits = coverage(json.loads(Path(requirements_path).read_text()), times, receipt.get("duration"))
    if hits != receipt.get("coverage"):
        raise ValueError("receipt coverage does not match panel times")
    images = []
    for i, panel in enumerate(panels, 1):
        expected = f"panel_{i:03d}.png"
        if panel.get("file") != expected:
            raise ValueError("panels must use consecutive neutral filenames")
        path = bundle / expected
        if path.is_symlink() or panel.get("sha256") != digest(path):
            raise ValueError(f"changed panel: {expected}")
        with Image.open(path) as image:
            if image.format != "PNG" or list(image.size) != panel.get("size"):
                raise ValueError(f"invalid panel image: {expected}")
            images.append(image.convert("RGB"))
    sheet = bundle / "storyboard.png"
    if sheet.is_symlink() or receipt.get("sheet_sha256") != digest(sheet):
        raise ValueError("changed storyboard sheet")
    expected = compose(images, times)
    with Image.open(sheet) as actual:
        if actual.size != expected.size or actual.convert("RGB").tobytes() != expected.tobytes():
            raise ValueError("sheet does not contain the declared panels in order")
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle")
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args()
    try:
        hits = verify(args.bundle, args.requirements, args.source)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"storyboard_check: FAIL: {exc}")
        return 1
    print(f"storyboard_check: PASS: {len(hits)} declared moments covered; integrity only, not a story/safety verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
