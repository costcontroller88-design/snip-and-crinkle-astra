"""Stored-frame folders with a code stamp (audit F2, 18 Oct 2026).

A slow pass (for example `--hires` at 3x) saves drawings as <folder>/dNNNNN.png and the render reads them back. A
stored drawing is used only when the folder's STAMP equals the current hash of the script and every repo module it
imports (found by tools/handover_check.modules; tools/ itself is left out, it draws nothing). So a code change can
never mix old drawings into a new render: a stale or unstamped folder is a miss, and the frame is drawn fresh.

    framestore.begin(folder, script)      before the pass: makes the folder and clears its stamp (a half-finished
                                          pass is never used)
    framestore.path(folder, d)            where drawing d goes
    framestore.finish(folder, script)     after the last drawing: writes the stamp
    framestore.load(folder, d, script)    the stored drawing (RGB), or None: missing, unstamped or stale; the first
                                          stale or unstamped miss per folder prints one warning line
    python3 episodes/framestore.py <script> [folder]    prints the hash, and whether the folder's stamp matches
"""
import functools
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
STAMP = "STAMP"
_warned = set()


def hashed_files(script):
    """The script and its repo imports that the stamp covers (tools/ left out)."""
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    from handover_check import modules
    return [f for f in modules(os.path.abspath(script)) if os.path.dirname(f) != TOOLS]


@functools.lru_cache(maxsize=None)
def code_hash(script):
    h = hashlib.sha256()
    for f in hashed_files(script):
        h.update(os.path.relpath(f, ROOT).encode())
        with open(f, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def path(folder, d):
    return os.path.join(folder, f"d{d:05d}.png")


def stamp_of(folder):
    try:
        with open(os.path.join(folder, STAMP), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def begin(folder, script):
    os.makedirs(folder, exist_ok=True)
    try:
        os.remove(os.path.join(folder, STAMP))
    except FileNotFoundError:
        pass


def finish(folder, script):
    tmp = os.path.join(folder, STAMP + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(code_hash(script))
    os.replace(tmp, os.path.join(folder, STAMP))


def load(folder, d, script):
    p = path(folder, d)
    if not os.path.exists(p):
        return None
    if stamp_of(folder) != code_hash(script):
        if folder not in _warned:
            _warned.add(folder)
            why = "unstamped" if stamp_of(folder) is None else "stale (the code changed since)"
            print(f"framestore: {os.path.relpath(folder, ROOT)} is {why}; drawing those frames fresh "
                  f"(refill it with the script's --hires pass)", file=sys.stderr, flush=True)
        return None
    from PIL import Image
    return Image.open(p).convert("RGB")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: framestore.py <script> [folder]")
    print("hash", code_hash(sys.argv[1]))
    if len(sys.argv) == 3:
        s = stamp_of(sys.argv[2])
        print("stamp", s or "none", "MATCH" if s == code_hash(sys.argv[1]) else "NO MATCH")
