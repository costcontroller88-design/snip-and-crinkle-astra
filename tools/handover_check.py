"""The animator's last command before handing over a render chain (agent ratings 8 Oct: M6, M11, M12, M13).

    python3 tools/handover_check.py episodes/ep12_tidy.py            the animator runs this last, on the final code
    python3 tools/handover_check.py episodes/ep12_tidy.py --verify   the first link of the Lead's render chain

Full mode, in order (exit 1 on any failure):
  1. audio: runs `<script> --audio`, then the same loudness (-14 ±1 LUFS) and silent-gap test (-38 dB, 0.25 s) as
     tools/check_video.py on the newest .wav it wrote under build/ (M13: a failed render costs a round).
  2. `<script> --check` on the final code; any printed line containing FAIL fails (M12).
  3. key sizes (M11): every row of the plan's key actions table needs `--check` lines `keysize <t> <pct>` (the key
     object's measured width as % of the frame width, from its mask) at ≥2 times inside its span, each at least the
     plan's Size. The plan is reviews/<epNN>_short_plan.md for a Short script, else reviews/<epNN>_plan.md.
     Audit M4 (v3.8: Shorts are cut from the episode and have no plan of their own): a `*short*` script with no
     reviews/<epNN>_short_plan.md skips the episode plan's key-action rows (their times are episode times) and needs
     ≥2 `keysize` lines, each ≥10 (% of the frame width). Step 4 still reads the episode plan; step 3b stays.
  3b. Shorts safe zones (M42, audit M5): in a script whose name has "short", every `keysize <t>` time needs a
     `safezone <t> <object> ok` line (tools/safezone.py); a missing one fails, and a FAIL line fails in step 2.
  4. the plan's measured checks table: no estimate left, no measured value under its Need (M26-M29).
  5. writes build/handover/<script>.ok with a hash of the script, the repo modules it imports (recursive; found
     under ROOT, ROOT/episodes, ROOT/tools; audit M3: a parallel build of another script no longer breaks this .ok)
     and the plan.
--verify fails if that file is missing or any of those or the plan changed since, so nothing unchecked gets rendered.
    python3 tools/handover_check.py episodes/ep11_short_transform.py --modules     prints the hashed module list
"""
import ast
import glob
import hashlib
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from check_video import audio_stats  # noqa: E402
from plan_check import find, span, tables, num, measured, measure_fails  # noqa: E402


def plan_for(script):
    m = re.match(r"(ep\d+)", os.path.basename(script))
    if not m:
        return None
    short = os.path.join(ROOT, "reviews", f"{m.group(1)}_short_plan.md")
    if "short" in os.path.basename(script) and os.path.exists(short):
        return short
    p = os.path.join(ROOT, "reviews", f"{m.group(1)}_plan.md")
    return p if os.path.exists(p) else None


def has_own_short_plan(script):
    m = re.match(r"(ep\d+)", os.path.basename(script))
    return bool(m) and os.path.exists(os.path.join(ROOT, "reviews", f"{m.group(1)}_short_plan.md"))


def modules(script):
    """The script plus every repo module it imports, recursively (audit M3). Modules are looked up as <name>.py under
    ROOT, ROOT/episodes and ROOT/tools; anything else (stdlib, numpy, PIL) is not part of the hash."""
    seen, todo = [], [os.path.abspath(script)]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.append(f)
        try:
            tree = ast.parse(open(f, encoding="utf-8").read())
        except (OSError, SyntaxError):
            continue
        for n in ast.walk(tree):
            names = [a.name for a in n.names] if isinstance(n, ast.Import) else \
                [n.module] if isinstance(n, ast.ImportFrom) and n.module and not n.level else []
            for name in names:
                for d in (ROOT, os.path.join(ROOT, "episodes"), os.path.join(ROOT, "tools")):
                    p = os.path.join(d, name.split(".")[0] + ".py")
                    if os.path.exists(p):
                        todo.append(p)
                        break
    return sorted(seen)


def code_hash(plan, script):
    h = hashlib.sha256()
    for f in modules(script) + ([plan] if plan else []):
        h.update(os.path.relpath(f, ROOT).encode())
        h.update(open(f, "rb").read())
    return h.hexdigest()


def run(script, flag):
    r = subprocess.run([sys.executable, script, flag], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    script = os.path.abspath(args[0])
    plan = plan_for(script)
    ok_file = os.path.join(ROOT, "build", "handover", os.path.basename(script) + ".ok")
    if "--modules" in args:
        print("\n".join(os.path.relpath(f, ROOT) for f in modules(script) + ([plan] if plan else [])))
        return
    if "--verify" in args:
        if not os.path.exists(ok_file):
            sys.exit("FAIL no handover check on record: the animator runs tools/handover_check.py last")
        if open(ok_file).read().split()[0] != code_hash(plan, script):
            sys.exit("FAIL code or plan changed after the handover check: run it again before rendering")
        print("handover verify: PASS")
        return
    fails = []
    # 1. audio
    t0 = time.time()
    rc, out = run(script, "--audio")
    wavs = [w for w in glob.glob(os.path.join(ROOT, "build", "**", "*.wav"), recursive=True)
            if os.path.getmtime(w) >= t0 - 1]
    if rc or not wavs:
        fails.append(f"--audio did not write a .wav under build/ (exit {rc}): {out.strip()[-200:]}")
    else:
        wav = max(wavs, key=os.path.getmtime)
        lufs, silences = audio_stats(wav)
        print(f"audio {os.path.relpath(wav, ROOT)}: {lufs} LUFS; silent gaps >0.25 s: {silences or 'none'}")
        if lufs is None or abs(lufs + 14) > 1.0:
            fails.append(f"loudness {lufs} LUFS (-14 ±1)")
        if silences:
            fails.append(f"silent gaps at {silences}")
    # 2. the whole --check on the final code
    rc, out = run(script, "--check")
    print(out.strip())
    if rc:
        fails.append(f"--check exited {rc}")
    fails += [f"--check: {ln.strip()}" for ln in out.splitlines() if "FAIL" in ln]
    # 3. key object sizes against the plan
    sizes = [(float(a), float(b)) for a, b in re.findall(r"keysize\s+([\d.]+)\s+([\d.]+)", out)]
    keys = find(tables(open(plan, encoding="utf-8").read()), "key action", "uncovered") if plan else None
    if "short" in os.path.basename(script) and not has_own_short_plan(script):
        # audit M4: a Short cut from the episode has no plan of its own; the episode plan's rows are episode times
        if len(sizes) < 2 or min(p for _, p in sizes) < 10:
            fails.append(f"Short without its own plan: needs ≥2 `keysize` lines each ≥10, got {[p for _, p in sizes]}")
    elif not keys:
        fails.append(f"no key actions table in {plan or 'the plan (not found)'}: key sizes not checked")
    else:
        for r in keys[1]:
            sp, need = span(r[1]) if len(r) > 1 else None, num(r[3]) if len(r) > 3 else None
            if not sp or need is None:
                continue
            got = [p for t, p in sizes if sp[0] - 0.05 <= t <= sp[1] + 0.05]
            tag = f"key action '{r[0][:30]}' {sp[0]:g}-{sp[1]:g} s"
            if len(got) < 2:
                fails.append(f"{tag}: {len(got)} keysize line(s) from --check (needs ≥2)")
            elif min(got) < need:
                fails.append(f"{tag}: measured {min(got):.1f}% < plan {need:g}%")
    if "short" in os.path.basename(script):
        zoned = [float(a) for a in re.findall(r"safezone\s+([\d.]+)", out)]
        for t, _ in sizes:
            if not any(abs(t - z) < 0.011 for z in zoned):
                fails.append(f"keysize {t:g}: no 'safezone {t:g} <object> ok' line from --check (M42; tools/safezone.py)")
    rows = measured(tables(open(plan, encoding="utf-8").read())) if plan else None
    if rows is None:
        fails.append("no measured checks table in the plan")
    else:
        fails += measure_fails(rows, allow_estimates=False)
    for f in fails:
        print("FAIL", f)
    if fails:
        sys.exit(f"handover_check: {len(fails)} failure(s); fix them, don't list them (M6)")
    os.makedirs(os.path.dirname(ok_file), exist_ok=True)
    with open(ok_file, "w") as fh:
        fh.write(code_hash(plan, script) + "\n")
    print("handover_check: PASS; render chain starts with: python3 tools/handover_check.py",
          os.path.relpath(script, ROOT), "--verify &&")


if __name__ == "__main__":
    main()
