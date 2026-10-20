"""Read-only production evidence checker. Never writes live gates or launches agents.

    python3 tools/pipeline_check.py template build/run/manifest.json
    python3 tools/pipeline_check.py check build/run/manifest.json

This validates documented evidence and its binding to current files. It does not
authenticate reviewer identities, interpret stories, or certify safety itself.
"""
import argparse
import hashlib
import json
from pathlib import Path

# check: (required artifacts, prerequisites, declared reviewer role)
CHECKS = {
    "story_card": (("brief", "card"), (), "story-designer"),
    "plan_safety": (("card", "stage"), ("story_card",), "safety-checker"),
    "clearance": (("stage", "rough"), ("story_card",), "script"),
    "framing": (("stage", "rough"), ("story_card",), "script"),
    "coverage": (("stage", "moments", "storyboard"), ("clearance", "framing"), "script"),
    "storyboard_review": (("storyboard",), ("coverage",), "fresh-eyes-reviewer"),
    "storyboard_match": (("card", "storyboard", "storyboard_retelling"), ("storyboard_review",), "story-comparison"),
    "episode_qa": (("episode", "episode_source"), ("plan_safety", "storyboard_match"), "script"),
    "short1_qa": (("short1", "short1_source"), ("episode_qa",), "script"),
    "short2_qa": (("short2", "short2_source"), ("episode_qa",), "script"),
    "episode_review": (("episode",), ("episode_qa",), "fresh-eyes-reviewer"),
    "short1_review": (("short1",), ("short1_qa",), "fresh-eyes-reviewer"),
    "short2_review": (("short2",), ("short2_qa",), "fresh-eyes-reviewer"),
    "packaging": (("episode", "short1", "short2", "package"),
                  ("episode_review", "short1_review", "short2_review"), "packaging"),
    "final_safety": (("episode", "short1", "short2", "package"),
                     ("packaging", "plan_safety"), "safety-checker"),
}
ARTIFACTS = sorted({a for inputs, _, _ in CHECKS.values() for a in inputs})


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bound_file(root, name):
    if not isinstance(name, str) or not name:
        raise ValueError("missing file path")
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("file must exist inside the run directory")
    return path


def evaluate(manifest, root):
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ValueError("manifest version must be 1")
    root = Path(root)
    makers, artifacts, evidence = (manifest.get(k) for k in ("makers", "artifacts", "evidence"))
    if (not isinstance(makers, list) or not makers or
            not all(isinstance(m, str) and m.strip() for m in makers) or
            not isinstance(artifacts, dict) or not isinstance(evidence, dict)):
        raise ValueError("makers, artifacts and evidence are required")
    makers = {m.strip().casefold() for m in makers}
    results, hashes = {}, {}
    for name in ARTIFACTS:
        try:
            hashes[name] = sha256(bound_file(root, artifacts.get(name)))
        except (OSError, ValueError):
            hashes[name] = None
    for name, (inputs, prerequisites, role) in CHECKS.items():
        reasons, rec = [], evidence.get(name)
        if not isinstance(rec, dict):
            rec = {}
        if rec.get("result") != "PASS":
            reasons.append("missing PASS evidence")
        if rec.get("role") != role:
            reasons.append("wrong or missing evidence role")
        if rec.get("override"):
            reasons.append("overrides do not count as acceptance evidence")
        try:
            if sha256(bound_file(root, rec.get("report"))) != rec.get("report_sha256"):
                reasons.append("report changed since evidence was recorded")
        except (OSError, ValueError):
            reasons.append("missing evidence report")
        bound = rec.get("inputs")
        if not isinstance(bound, dict):
            bound = {}
        if set(bound) != set(inputs):
            reasons.append("input bindings do not match this check's contract")
        for artifact in inputs:
            if not hashes[artifact] or bound.get(artifact) != hashes[artifact]:
                reasons.append(f"missing or stale input: {artifact}")
        if role in ("fresh-eyes-reviewer", "safety-checker"):
            reviewer = rec.get("reviewer", "")
            if not isinstance(reviewer, str) or not reviewer.strip() or reviewer.strip().casefold() in makers:
                reasons.append("independent reviewer identity required")
        if role == "fresh-eyes-reviewer":
            if rec.get("blind") is not True:
                reasons.append("blind-review declaration required")
            if type(rec.get("round")) is not int or not 1 <= rec["round"] <= 2:
                reasons.append("review round must be 1 or 2")
            if name != "storyboard_review":
                for metric in ("overall", "clarity"):
                    value = rec.get(metric)
                    if type(value) not in (int, float) or not 8 <= value <= 10:
                        reasons.append(f"{metric} must be at least 8/10")
        if name == "storyboard_match" and rec.get("match") is not True:
            reasons.append("independent retelling comparison has not matched")
        if name == "storyboard_review" and rec.get("report_sha256") != hashes["storyboard_retelling"]:
            reasons.append("review report must be the current storyboard retelling")
        if role == "safety-checker" and (type(rec.get("structural_fixes")) is not int or rec["structural_fixes"] != 0):
            reasons.append("safety target requires no structural fix")
        for previous in prerequisites:
            if results[previous]["status"] != "DOCUMENTED_PASS":
                reasons.append(f"prerequisite not accepted: {previous}")
        results[name] = {"status": "BLOCKED" if reasons else "DOCUMENTED_PASS", "reasons": reasons}
    ready = all(r["status"] == "DOCUMENTED_PASS" for r in results.values())
    return {"ready_for_owner_review": ready, "checks": results,
            "notice": "Documented evidence only; reviewer authenticity and judgments require independent verification. "
                      "This does not record gates or authorize publication."}


def template():
    return {"version": 1, "makers": ["Astra"], "artifacts": {a: "" for a in ARTIFACTS}, "evidence": {}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("template", "check"))
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    if args.command == "template":
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        with args.manifest.open("x") as stream:
            json.dump(template(), stream, indent=2)
            stream.write("\n")
        return 0
    try:
        result = evaluate(json.loads(args.manifest.read_text()), args.manifest.parent)
    except (ValueError, OSError) as exc:
        print(json.dumps({"ready_for_owner_review": False, "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["ready_for_owner_review"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
