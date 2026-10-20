"""Adversarial evidence fixtures, not production gate records."""
import copy
from pathlib import Path
import tempfile
import unittest

import pipeline_check as pipeline


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = pipeline.template()
        for a in pipeline.ARTIFACTS:
            (self.root / a).write_text("synthetic " + a)
            self.manifest["artifacts"][a] = a
        for name, (inputs, _, role) in pipeline.CHECKS.items():
            report = self.root / (name + ".txt")
            report.write_text("Synthetic fixture; this is not a real review.")
            self.manifest["evidence"][name] = {
                "result": "PASS", "role": role, "report": report.name,
                "report_sha256": pipeline.sha256(report),
                "inputs": {a: pipeline.sha256(self.root / a) for a in inputs},
                "reviewer": "independent-fixture", "blind": True, "round": 1,
                "overall": 8, "clarity": 8, "match": True, "structural_fixes": 0}
        self.manifest["artifacts"]["storyboard_retelling"] = "storyboard_review.txt"
        self.manifest["evidence"]["storyboard_match"]["inputs"]["storyboard_retelling"] = pipeline.sha256(
            self.root / "storyboard_review.txt")

    def check(self):
        return pipeline.evaluate(self.manifest, self.root)

    def test_complete_documentary_fixture(self):
        self.assertTrue(self.check()["ready_for_owner_review"])

    def test_empty_template_blocks(self):
        result = pipeline.evaluate(pipeline.template(), self.root)
        self.assertFalse(result["ready_for_owner_review"])
        self.assertEqual(sum(r["status"] == "BLOCKED" for r in result["checks"].values()), 15)

    def test_changed_video_invalidates_reviews_and_release(self):
        (self.root / "episode").write_text("changed")
        result = self.check()
        self.assertEqual(result["checks"]["episode_review"]["status"], "BLOCKED")
        self.assertEqual(result["checks"]["final_safety"]["status"], "BLOCKED")

    def test_changed_report_fails(self):
        (self.root / "plan_safety.txt").write_text("edited")
        self.assertFalse(self.check()["ready_for_owner_review"])

    def test_wrong_identity_role_blindness_and_scores_fail(self):
        for field, value in (("reviewer", " astra "), ("role", "script"), ("blind", False),
                             ("clarity", 7), ("overall", float("nan")), ("round", 3),
                             ("round", True), ("override", "owner approved")):
            with self.subTest(field=field, value=value):
                old = copy.deepcopy(self.manifest)
                self.manifest["evidence"]["episode_review"][field] = value
                self.assertFalse(self.check()["ready_for_owner_review"])
                self.manifest = old

    def test_safety_fix_or_missing_short_blocks(self):
        self.manifest["evidence"]["plan_safety"]["structural_fixes"] = 1
        self.assertFalse(self.check()["ready_for_owner_review"])
        self.manifest["evidence"]["plan_safety"]["structural_fixes"] = 0
        (self.root / "short2").unlink()
        self.assertFalse(self.check()["ready_for_owner_review"])

    def test_story_mismatch_blocks_full_build_evidence(self):
        self.manifest["evidence"]["storyboard_match"]["match"] = False
        result = self.check()
        self.assertIn("prerequisite not accepted: storyboard_match", result["checks"]["episode_qa"]["reasons"])

    def test_new_retelling_invalidates_old_comparison(self):
        report = self.root / "storyboard_review.txt"
        report.write_text("a new independent retelling")
        self.manifest["evidence"]["storyboard_review"]["report_sha256"] = pipeline.sha256(report)
        self.assertEqual(self.check()["checks"]["storyboard_match"]["status"], "BLOCKED")

    def test_missing_binding_and_path_escape_fail(self):
        self.manifest["evidence"]["storyboard_review"]["inputs"] = {}
        self.assertFalse(self.check()["ready_for_owner_review"])
        self.manifest["artifacts"]["card"] = "../outside.txt"
        self.assertIn("missing or stale input: card", self.check()["checks"]["story_card"]["reasons"])


if __name__ == "__main__":
    unittest.main()
