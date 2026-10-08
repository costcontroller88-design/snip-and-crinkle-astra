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
  4. writes build/handover/<script>.ok with a hash of every .py file in the repo and the plan.
--verify fails if that file is missing or any code or the plan changed since, so nothing unchecked gets rendered.
"""
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
from plan_check import find, span, tables, num  # noqa: E402


def plan_for(script):
    m = re.match(r"(ep\d+)", os.path.basename(script))
    if not m:
        return None
    short = os.path.join(ROOT, "reviews", f"{m.group(1)}_short_plan.md")
    if "short" in os.path.basename(script) and os.path.exists(short):
        return short
    p = os.path.join(ROOT, "reviews", f"{m.group(1)}_plan.md")
    return p if os.path.exists(p) else None


def code_hash(plan):
    h = hashlib.sha256()
    files = sorted(glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True))
    for f in files + ([plan] if plan else []):
        if "/venv" in f or "/build/" in f or "__pycache__" in f:
            continue
        h.update(f.encode())
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
    if "--verify" in args:
        if not os.path.exists(ok_file):
            sys.exit("FAIL no handover check on record: the animator runs tools/handover_check.py last")
        if open(ok_file).read().split()[0] != code_hash(plan):
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
    if not keys:
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
    for f in fails:
        print("FAIL", f)
    if fails:
        sys.exit(f"handover_check: {len(fails)} failure(s); fix them, don't list them (M6)")
    os.makedirs(os.path.dirname(ok_file), exist_ok=True)
    with open(ok_file, "w") as fh:
        fh.write(code_hash(plan) + "\n")
    print("handover_check: PASS; render chain starts with: python3 tools/handover_check.py",
          os.path.relpath(script, ROOT), "--verify &&")


if __name__ == "__main__":
    main()
