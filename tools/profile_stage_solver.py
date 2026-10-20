"""Bounded, reproducible staging profiles. No tables/gates/cache files are written.

    python3 tools/profile_stage_solver.py build/astra/stage-profile.json --timeout 45

Each case has its own process and empty private pose cache. The first two solves
are unprofiled cold/warm measurements; a third captures hotspots. Timeouts retain
any completed measurements and are not reported as successful solves.
"""
import argparse
import cProfile
import hashlib
import json
from pathlib import Path
import pstats
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CASES = ("literal", "draw", "refusal")


def worker(case):
    sys.path[:0] = [str(ROOT), str(ROOT / "episodes")]
    import stage_kit as sk
    with tempfile.TemporaryDirectory(prefix="snc_stage_profile_") as temp:
        sk.CACHE = str(Path(temp) / "poses.json")
        sk._DISK.update(loaded=False, dirty=False, data={})
        table = sk.Table("fixture", "playroom" if case == "literal" else "porch",
                         "land" if case == "literal" else "vert")
        if case == "literal":
            table.start = {"Snip": ("C", "front")}
            args = (.5, 1.5, "Snip", "hold", "")
        else:
            table.start = {"Snip": ("x:400", "right"), "Crinkle": ("x:1300", "left"),
                           "marker": ("Snip", ""), "lantern": ("C", "")}
            args = (.5, 1.9, "Snip", "draw", "lantern.eye_l") if case == "draw" else \
                   (0, .5, "Snip", "draw", "lantern.eye_l")

        def solve():
            try:
                new, rows, shot = sk.solve(table, *args)
                return {"result": "ACCEPTED", "rows": rows, "shot": shot,
                        "remaining_problems": sk.Sim(new).problems()}
            except sk.Refused as exc:
                return {"result": "REFUSED", "reason": str(exc)}

        for phase in ("cold", "warm", "profiled"):
            profile = cProfile.Profile() if phase == "profiled" else None
            if profile:
                profile.enable()
            started = time.perf_counter()
            outcome = solve()
            seconds = time.perf_counter() - started
            if profile:
                profile.disable()
            record = {"case": case, "phase": phase, "seconds": seconds, "outcome": outcome,
                      "outcome_sha256": hashlib.sha256(json.dumps(outcome, sort_keys=True).encode()).hexdigest()}
            if profile:
                stats = pstats.Stats(profile)
                hot = sorted(stats.stats.items(), key=lambda item: item[1][3], reverse=True)[:15]
                record["hotspots"] = [{"file": str(Path(key[0]).relative_to(ROOT)) if str(key[0]).startswith(str(ROOT)) else key[0],
                                       "line": key[1], "function": key[2], "calls": val[1],
                                       "self_seconds": val[2], "cumulative_seconds": val[3]} for key, val in hot]
            print(json.dumps(record), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--worker", choices=CASES)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker)
        return 0
    if args.output is None or not 1 <= args.timeout <= 60:
        parser.error("output required; timeout must be between 1 and 60 seconds per case")
    if args.output.exists():
        parser.error("output exists; use a new report path")
    cases = []
    for case in CASES:
        command = [sys.executable, __file__, "--worker", case]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
            stdout, error = result.stdout, result.stderr
            status = "COMPLETE" if result.returncode == 0 else "ERROR"
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            error, status = "per-case time limit exceeded", "TIMEOUT"
        records = []
        for line in stdout.splitlines():
            try:
                records.append(json.loads(line))
            except ValueError:
                pass
        consistent = len({r["outcome_sha256"] for r in records}) <= 1
        cases.append({"case": case, "status": status, "consistent": consistent, "runs": records, "error": error})
        print(case, status, [(r["phase"], round(r["seconds"], 4), r["outcome"]["result"]) for r in records], flush=True)
    files = list(ROOT.glob("*.py")) + list((ROOT / "episodes").glob("*.py")) + [Path(__file__)]
    report = {"timeout_seconds": args.timeout, "cases": cases,
              "code_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if all(c["status"] == "COMPLETE" and c["consistent"] for c in cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
