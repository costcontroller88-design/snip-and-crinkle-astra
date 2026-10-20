"""Compare optimized geometry with the frozen original algorithm, including holes/edges."""
import math
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "episodes"))
import stage_kit as sk


def reference_gap(a, b, need):
    best, k = need + 2.0, int((need + 2) // sk.BAND) + 1
    for s in range(-k, k + 1):
        b0, b1 = sk._shift(b[0], s), sk._shift(b[1], s)
        both = ~np.isnan(a[0]) & ~np.isnan(b0)
        if not both.any():
            continue
        gx = float(np.maximum(np.maximum(b0 - a[1], a[0] - b1), 0.0)[both].min())
        best = min(best, math.hypot(gx, max(0.0, (abs(s) - 1) * sk.BAND)))
        if best == 0.0:
            break
    return best


class GapTests(unittest.TestCase):
    def test_seeded_profile_equivalence(self):
        rng = np.random.default_rng(20261020)
        for i in range(512):
            n = (1, 8, 300)[i % 3]
            a0, b0 = rng.uniform(-100, 100, (2, n))
            a1, b1 = a0 + rng.uniform(0, 30, n), b0 + rng.uniform(0, 30, n)
            for lo, hi in ((a0, a1), (b0, b1)):
                holes = rng.random(n) < .7
                lo[holes] = hi[holes] = np.nan
            need = (0, 1, 10, 30, 40)[i % 5]
            a, b = (a0, a1), (b0, b1)
            with self.subTest(i=i):
                self.assertEqual(sk.gap(a, b, need), reference_gap(a, b, need))

    def test_empty_touching_and_far_profiles(self):
        blank = (np.full(8, np.nan), np.full(8, np.nan))
        a = (np.zeros(8), np.ones(8) * 10)
        touching = (np.ones(8) * 10, np.ones(8) * 20)
        far = (np.ones(8) * 100, np.ones(8) * 110)
        for left, right in ((blank, blank), (a, blank), (a, touching), (a, far)):
            for need in (0, 10, 40):
                self.assertEqual(sk.gap(left, right, need), reference_gap(left, right, need))

    def test_real_dependency_closure_includes_root_character_and_algorithm(self):
        from handover_check import modules
        files = {Path(p).resolve() for p in modules(sk.__file__)}
        self.assertIn(Path(sk.ROOT) / "characters.py", files)
        self.assertIn(Path(sk.ROOT) / "paperlib.py", files)
        self.assertIn(Path(sk.__file__).resolve(), files)

    def test_changed_dependency_rejects_persisted_poses(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "characters.py"
            source.write_text("original geometry")
            cache = Path(temp) / "poses.json"
            with patch("handover_check.modules", return_value=[str(source)]), \
                    patch.object(sk, "CACHE", str(cache)), \
                    patch.object(sk, "_DISK", {"loaded": False, "dirty": False, "data": {}}):
                key = sk._code_key()
                cache.write_text(json.dumps({"key": key, "data": {"sentinel": "old pose"}}))
                self.assertEqual(sk._disk(), {"sentinel": "old pose"})
                source.write_text("changed geometry")
                self.assertNotEqual(sk._code_key(), key)
                sk._DISK["dirty"] = True
                with self.assertRaisesRegex(sk.Refused, "dependencies changed"):
                    sk.save_cache()
                self.assertEqual(json.loads(cache.read_text())["key"], key)
                sk._DISK.update(loaded=False, dirty=False, data={})
                self.assertEqual(sk._disk(), {})
                sk._DISK["data"]["sentinel"] = "fresh pose"
                sk._DISK["dirty"] = True
                sk.save_cache()
                self.assertEqual(json.loads(cache.read_text())["key"], sk._code_key())
                self.assertFalse(Path(str(cache) + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
