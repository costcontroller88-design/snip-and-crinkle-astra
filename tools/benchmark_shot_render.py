"""Reproducible engineering fixture, not a story or safety/clarity review.

    python3 tools/benchmark_shot_render.py build/astra/shot-trial-01

Three 0.2-second rig shots; cold, warm, middle-shot edit and clean rebuild.
All images/audio are generated in this project. Writes no live gates or reviews.
"""
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "episodes")]
import shot_render as sr
import stage_kit as sk


def main(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    shots = [{"id": f"s{i}", "start": i * 3, "frames": 3, "seed": 1,
              "config": {"facing": "front", "mark": "C"}} for i in range(3)]
    stages = {}

    def draw(shot, index):
        key = json.dumps(shot["config"], sort_keys=True)
        if key not in stages:
            table = sk.Table("fixture", "playroom", "land")
            table.start = {"Snip": (shot["config"]["mark"], shot["config"]["facing"])}
            table.beats = [(0, .2, "Snip", "hold", "")]
            table.shots = [(0, .2, "W")]
            stages[key] = sk.Stage(table)
        return stages[key].still((index - shot["start"]) / sr.DPS)

    dependencies = (list(ROOT.glob("*.py")) + list((ROOT / "episodes").glob("*.py")) +
                    list((ROOT / "assets/fonts").glob("*.ttf")) + [Path(__file__)])
    results = {}
    for label in ("cold", "warm", "edited", "clean"):
        if label == "edited":
            shots[1]["config"]["facing"] = "right"
        cache = output / ("clean-cache" if label == "clean" else "cache")
        results[label] = sr.render(shots, draw, dependencies, cache)
        print(label, json.dumps({k: results[label][k] for k in ("seconds", "rendered_drawings")}), flush=True)
    assert [results[k]["rendered_drawings"] for k in results] == [9, 0, 3, 9]
    assert [s["cache_hit"] for s in results["edited"]["shots"]] == [True, False, True]
    assert results["edited"]["frame_sha256"] == results["clean"]["frame_sha256"]
    wav = output / "tone.wav"
    with wave.open(str(wav), "wb") as stream:
        stream.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
        stream.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 48000)))
                                   for i in range(48000)))
    for label in ("edited", "clean"):
        sr.encode(results[label], wav, output / f"{label}.mp4")
    def video_hashes(path):
        text = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:v:0",
                                        "-f", "framemd5", "-"], text=True)
        return [line for line in text.splitlines() if not line.startswith("#")]
    def audio_bytes(path):
        return subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
                                        "-f", "s16le", "-acodec", "pcm_s16le", "-"])
    assert video_hashes(output / "edited.mp4") == video_hashes(output / "clean.mp4")
    assert audio_bytes(output / "edited.mp4") == audio_bytes(output / "clean.mp4")
    report = {"results": results, "frame_pixels_equal": True, "decoded_video_equal": True,
              "decoded_audio_equal": True, "fixture_only": True}
    (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS: cold 9, warm 0, edited 3, clean 9 drawings; cached and clean video/audio agree.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
