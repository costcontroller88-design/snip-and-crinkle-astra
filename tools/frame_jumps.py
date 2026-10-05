"""Measure the biggest frame-to-frame change (same metric as tools/check_video.py) inside time
windows, straight from render_frame(), without a full render.

    python3 tools/frame_jumps.py episodes/ep06_xxx.py 4.4 5.6  6.4 8.0

Keep every window below ~18 here (the encoded video adds ~1-2). Zooms or fast vertical moves over
fine stripes (zebra crossings, gingham, tiles) are the usual cause; slow them down (< ~0.35 zoom/s),
ease camera shakes in and out, or pan sideways instead.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_frames import load  # noqa: E402

if __name__ == "__main__":
    m = load(sys.argv[1])
    a = [float(x) for x in sys.argv[2:]]

    def g(t):
        return np.asarray(m.render_frame(t).convert("L").resize((270, 480)), np.float32)
    for t0, t1 in zip(a[::2], a[1::2]):
        i0, i1 = round(t0 * 30), round(t1 * 30)
        prev, worst = g(i0 / 30), (0.0, 0.0)
        for i in range(i0 + 1, i1 + 1):
            cur = g(i / 30)
            worst = max(worst, (float(np.abs(cur - prev).mean()), i / 30))
            prev = cur
        print(f"{t0:.2f}-{t1:.2f}: max {worst[0]:.1f} at {worst[1]:.2f}s")
