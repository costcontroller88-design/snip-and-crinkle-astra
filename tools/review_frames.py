"""Render chosen frames of an episode into one review sheet (480px wide each, 4 per row).

    python3 tools/review_frames.py episodes/ep06_xxx.py build/review.png 0.0 3.4 5.0 7.2

Look at these at full size before every full render: props hidden behind characters,
characters cut off at the frame edge and clutter are the most common bugs.
"""
import importlib.util
import os
import sys

from PIL import Image, ImageDraw


def load(path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec = importlib.util.spec_from_file_location("ep", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


if __name__ == "__main__":
    path, out, times = sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[3:]]
    m = load(path)
    w, h = 480, 853
    cols = min(4, len(times))
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8), rows * (h + 30)), "white")
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(times):
        im = m.render_frame(t).convert("RGB").resize((w, h), Image.LANCZOS)
        x, y = (i % cols) * (w + 8), (i // cols) * (h + 30)
        sheet.paste(im, (x, y + 28))
        d.text((x + 6, y + 6), f"{t:.2f}s", fill="black")
    sheet.save(out)
    print("wrote", out)
