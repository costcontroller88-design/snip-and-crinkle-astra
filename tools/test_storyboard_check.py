"""M82: temporary-file tests; no live story, agent or gate state is used."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image

import storyboard_check as sb


class StoryboardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="snc_storyboard_")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "table.md"
        self.source.write_text("synthetic fixture, not a story\n")
        self.requirements = {"version": 1, "moments": [
            {"id": name, "start": i, "end": i + 0.8}
            for i, name in enumerate(("cause", "problem", "lesson", "payoff"))]}
        self.req = self.root / "moments.json"
        self.req.write_text(json.dumps(self.requirements))
        self.times = [0.4, 1.4, 2.4, 3.4]
        self.out = self.root / "revision1"
        self.rendered = []

    def frame(self, t):
        self.rendered.append(t)
        return Image.new("RGB", (320, 180), (int(t * 50), 80, 170))

    def build(self):
        return sb.write_bundle(self.frame, self.times, 4, self.req, self.source, self.out)

    def verify(self):
        return sb.verify(self.out, self.req, self.source)

    def mutate_receipt(self, mutate):
        path = self.out / "receipt.json"
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data))

    def test_good_sheet_is_neutral_and_uses_exact_samples(self):
        path = self.build()
        self.assertEqual(self.rendered, self.times)
        self.assertEqual(self.verify(), {"cause": [1], "problem": [2], "lesson": [3], "payoff": [4]})
        self.assertEqual(path.name, "storyboard.png")
        with Image.open(path) as image:
            self.assertEqual(image.info, {})
            self.assertEqual(image.size, (1488, 616))
            self.assertEqual(image.getpixel((20, 20)), (20, 80, 170))
            self.assertEqual(image.getpixel((512, 20)), (70, 80, 170))

    def test_missing_moment_fails_before_render(self):
        self.times.pop(0)
        with self.assertRaisesRegex(ValueError, "missing panel for moment: cause"):
            self.build()
        self.assertEqual(self.rendered, [])
        self.assertFalse(self.out.exists())

    def test_omitted_required_declaration_fails(self):
        req = copy.deepcopy(self.requirements)
        req["moments"].pop()
        with self.assertRaisesRegex(ValueError, "missing required moments: payoff"):
            sb.coverage(req, self.times, 4)

    def test_extra_moment_is_checked(self):
        req = copy.deepcopy(self.requirements)
        req["moments"].append({"id": "reveal", "start": 3.6, "end": 3.8})
        with self.assertRaisesRegex(ValueError, "missing panel for moment: reveal"):
            sb.coverage(req, self.times, 4)

    def test_invalid_times_and_ranges_fail(self):
        for times in ([], [True], [-1], [float("nan")], [float("inf")], [4],
                      list(reversed(self.times)), [0.4, 0.4, 1.4, 2.4, 3.4]):
            with self.subTest(times=times), self.assertRaises(ValueError):
                sb.coverage(self.requirements, times, 4)
        for start, end in ((-1, 1), (2, 1), (0, 4), (False, 1), (0, float("nan"))):
            req = copy.deepcopy(self.requirements)
            req["moments"][0].update(start=start, end=end)
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                sb.coverage(req, self.times, 4)

    def test_duplicate_moment_ids_fail(self):
        req = copy.deepcopy(self.requirements)
        req["moments"].append(req["moments"][0])
        with self.assertRaisesRegex(ValueError, "unique"):
            sb.coverage(req, self.times, 4)

    def test_missing_or_changed_panel_fails(self):
        self.build()
        panel = self.out / "panel_001.png"
        panel.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "changed panel"):
            self.verify()
        panel.unlink()
        with self.assertRaises(OSError):
            self.verify()

    def test_stale_table_and_requirements_fail(self):
        self.build()
        for path in (self.source, self.req):
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            with self.assertRaisesRegex(ValueError, "stale or changed input"):
                self.verify()
            path.write_bytes(original)

    def test_sheet_pixels_checked_even_if_hash_updated(self):
        self.build()
        path = self.out / "storyboard.png"
        with Image.open(path) as image:
            image.putpixel((20, 20), (255, 0, 0))
            image.save(path)
        self.mutate_receipt(lambda data: data.update(sheet_sha256=sb.digest(path)))
        with self.assertRaisesRegex(ValueError, "sheet does not contain"):
            self.verify()

    def test_panel_order_and_path_escape_fail(self):
        self.build()
        self.mutate_receipt(lambda data: data["panels"][0].update(file="../table.md"))
        with self.assertRaisesRegex(ValueError, "neutral filenames"):
            self.verify()

    def test_declared_coverage_cannot_disagree_with_samples(self):
        self.build()
        self.mutate_receipt(lambda data: data["coverage"].update(cause=[2]))
        with self.assertRaisesRegex(ValueError, "coverage does not match"):
            self.verify()

    def test_existing_revision_is_preserved(self):
        self.build()
        original = (self.out / "receipt.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.build()
        self.assertEqual(original, (self.out / "receipt.json").read_bytes())

    def test_renderer_failure_leaves_no_completed_bundle(self):
        def broken(t):
            raise RuntimeError("render failed")
        with self.assertRaises(RuntimeError):
            sb.write_bundle(broken, self.times, 4, self.req, self.source, self.out)
        self.assertFalse(self.out.exists())
        self.assertEqual(list(self.root.glob(".storyboard-*")), [])

    def test_cli_exit_codes(self):
        self.build()
        cmd = [sys.executable, sb.__file__, str(self.out), "--requirements", str(self.req),
               "--source", str(self.source)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        (self.out / "panel_002.png").unlink()
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)

    def test_stage_command_uses_renderer_and_refuses_camera_gap(self):
        import stage
        stub = SimpleNamespace(still=self.frame, sim=SimpleNamespace(end=4),
                               table=SimpleNamespace(shots=[(0, 4, "W")]))
        args = ["fixture", str(self.req), "0.4,1.4,2.4,3.4", str(self.out)]
        with patch.object(stage.SK.Stage, "load", return_value=stub), \
                patch.object(stage.SK.Table, "path", return_value=str(self.source)):
            stage.cmd_covered_sheet(args)
            self.assertEqual(self.rendered, self.times)
            stub.table.shots = [(1, 4, "W")]
            args[-1] = str(self.root / "revision2")
            with self.assertRaises(SystemExit) as exc:
                stage.cmd_covered_sheet(args)
            self.assertEqual(exc.exception.code, 1)
            self.assertFalse(Path(args[-1]).exists())


if __name__ == "__main__":
    unittest.main()
