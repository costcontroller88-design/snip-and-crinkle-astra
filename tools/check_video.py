"""Objective quality checks for a rendered Short.

    python3 tools/check_video.py output/ep02_xxx.mp4                 (vertical Short, must loop)
    python3 tools/check_video.py output/x.mp4 --landscape --no-loop  (1920x1080 long-form or test scene)
    ... --cuts 3.0,5.2,8.95                                          (deliberate camera cuts: not "harsh")
    ... --dur 15-30                                                  (a transformation Short; a story Short 12-60)

Checks: duration, vertical size, loudness (YouTube ~ -14 LUFS), silent gaps,
the biggest frame-to-frame jump (harsh cuts), and the loop seam (last -> first frame).
Exits non-zero if a hard rule fails.
"""
import json
import re
import subprocess
import sys

import numpy as np


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type",
                          "-of", "json", path], capture_output=True, text=True).stdout
    return json.loads(out)


def audio_stats(path):
    err = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128,silencedetect=n=-38dB:d=0.25",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = re.findall(r"^\s+I:\s+(-?[\d.]+) LUFS", err, re.M)
    silences = re.findall(r"silence_start: ([\d.]+)", err)
    return (float(lufs[-1]) if lufs else None), [float(s) for s in silences]


def frame_stats(path, w=270, h=480):
    if LANDSCAPE:
        w, h = 480, 270
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    for c in CUTS:                       # ignore the frame changes right at a deliberate cut
        i = int(round(c * 30))
        d[max(0, i - 4):i + 4] = 0
    return len(fr), float(np.median(d)), float(d.max()), int(d.argmax()), float(np.abs(fr[-1] - fr[0]).mean())


def main(path):
    info = probe(path)
    dur = float(info["format"]["duration"])
    vid = next(s for s in info["streams"] if s["codec_type"] == "video")
    lufs, silences = audio_stats(path)
    n, med, mx, at, seam = frame_stats(path)
    fails = []
    print(f"file: {path}")
    print(f"size: {vid['width']}x{vid['height']}  duration: {dur:.2f}s  frames: {n}")
    print(f"loudness: {lufs} LUFS (target -14 ±1)")
    print(f"silent gaps >0.25s: {silences or 'none'}")
    print(f"frame change: median {med:.2f}, biggest {mx:.2f} at {at / 30:.2f}s (keep < 20 unless it's a deliberate cut)")
    print(f"loop seam (last->first): {seam:.2f} (seamless if within ~1.5x of median {med:.2f})")
    want = (1920, 1080) if LANDSCAPE else (1080, 1920)
    if (vid["width"], vid["height"]) != want:
        fails.append(f"not {want[0]}x{want[1]}")
    if not LANDSCAPE and not 12 <= dur <= 180:
        fails.append("duration outside 12–180s (YouTube Shorts limit)")
    if DUR and not DUR[0] <= dur <= DUR[1]:
        fails.append(f"duration outside {DUR[0]:g}-{DUR[1]:g}s (--dur)")
    if lufs is None or abs(lufs + 14) > 1.0:
        fails.append("loudness not -14±1 LUFS")
    if silences:
        fails.append("silent gaps")
    if mx > 20:
        fails.append(f"harsh jump at {at / 30:.2f}s")
    if LOOP and seam > max(3.0, 1.5 * med):
        fails.append("loop seam visible")
    print("RESULT:", "PASS" if not fails else "FAIL — " + "; ".join(fails))
    return 0 if not fails else 1


LANDSCAPE = "--landscape" in sys.argv
CUTS = ([float(x) for x in sys.argv[sys.argv.index("--cuts") + 1].split(",")] if "--cuts" in sys.argv else [])
LOOP = "--no-loop" not in sys.argv
DUR = ([float(x) for x in sys.argv[sys.argv.index("--dur") + 1].split("-")] if "--dur" in sys.argv else None)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
