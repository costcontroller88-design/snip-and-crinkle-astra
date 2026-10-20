"""Selective rendering tests use only generated temporary images and sound."""
import copy
import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "episodes"))
import shot_render as sr


class ShotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dep = self.root / "renderer.py"
        self.dep.write_text("synthetic renderer version 1")
        self.shots = [{"id": f"s{i}", "start": i * 3, "frames": 3, "seed": i,
                       "config": {"red": i * 60}} for i in range(3)]
        self.calls = []
        self.wav = self.root / "audio.wav"
        with wave.open(str(self.wav), "wb") as f:
            f.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            f.writeframes(b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / 48000)))
                                  for i in range(48000)))

    def draw(self, shot, index):
        self.calls.append((shot["id"], index))
        return Image.new("RGB", (16, 16), (shot["config"]["red"], index * 10, shot["seed"]))

    def run_render(self, cache="cache", draw=None):
        return sr.render(self.shots, draw or self.draw, [self.dep], self.root / cache, (16, 16))

    def test_cold_warm_and_local_edit_match_clean_pixels(self):
        cold = self.run_render()
        self.assertEqual(cold["rendered_drawings"], 9)
        self.calls.clear()
        warm = self.run_render()
        self.assertEqual(warm["rendered_drawings"], 0)
        self.assertEqual(self.calls, [])
        self.shots[1]["config"]["red"] = 111
        changed = self.run_render()
        self.assertEqual([s["cache_hit"] for s in changed["shots"]], [True, False, True])
        self.assertEqual(changed["rendered_drawings"], 3)
        self.assertEqual(changed["frame_sha256"], self.run_render("clean")["frame_sha256"])

    def test_seed_and_shared_dependency_invalidate(self):
        self.run_render()
        self.shots[2]["seed"] += 1
        self.assertEqual([s["cache_hit"] for s in self.run_render()["shots"]], [True, True, False])
        self.dep.write_text("same-process version 2")
        self.assertEqual(self.run_render()["rendered_drawings"], 9)

    def test_corrupt_missing_and_unstamped_shots_redraw(self):
        first = self.run_render()
        Path(first["frames"][0]).write_bytes(b"corrupt")
        Path(first["frames"][3]).unlink()
        (Path(first["frames"][6]).parent / "receipt.json").unlink()
        recovered = self.run_render()
        self.assertEqual(recovered["rendered_drawings"], 9)
        self.assertEqual(recovered["frame_sha256"], first["frame_sha256"])

    def test_failed_render_leaves_no_complete_shot_or_lock(self):
        def broken(shot, index):
            raise RuntimeError("intentional fixture failure")
        with self.assertRaises(RuntimeError):
            self.run_render(draw=broken)
        self.assertEqual(list((self.root / "cache").iterdir()), [])

    def test_dependency_change_during_draw_is_refused(self):
        def unstable(shot, index):
            self.dep.write_text(str(index))
            return self.draw(shot, index)
        with self.assertRaisesRegex(ValueError, "dependencies changed"):
            self.run_render(draw=unstable)
        self.assertEqual(list((self.root / "cache").iterdir()), [])

    def test_invalid_timeline_and_config_fail(self):
        for field, value in (("start", 4), ("frames", 0), ("seed", True), ("config", []), ("id", "s0")):
            before = copy.deepcopy(self.shots)
            self.shots[1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.run_render()
            self.shots = before

    def test_busy_cache_fails_without_breaking_lock(self):
        cache = self.root / "cache"
        cache.mkdir()
        lock = cache / ".writer.lock"
        lock.write_text("another writer")
        with self.assertRaises(FileExistsError):
            self.run_render()
        self.assertTrue(lock.exists())

    def test_encode_preserves_complete_output_and_rejects_short_audio(self):
        result = self.run_render()
        target = self.root / "out.mp4"
        self.assertEqual(sr.encode(result, self.wav, target), str(target))
        self.assertTrue(target.stat().st_size > 0)
        with self.assertRaisesRegex(ValueError, "output exists"):
            sr.encode(result, self.wav, target)
        with wave.open(str(self.wav), "wb") as f:
            f.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            f.writeframes(b"\x00\x00")
        with self.assertRaisesRegex(ValueError, "audio is shorter"):
            sr.encode(result, self.wav, self.root / "short.mp4")
        self.assertFalse((self.root / "short.mp4").exists())

    def test_encode_rechecks_cache_and_cleans_partial_output(self):
        result = self.run_render()
        Path(result["frames"][4]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "cached frame changed"):
            sr.encode(result, self.wav, self.root / "bad.mp4")
        self.assertFalse((self.root / "bad.mp4").exists())
        self.assertEqual(list(self.root.glob(".encode-*")), [])


if __name__ == "__main__":
    unittest.main()
