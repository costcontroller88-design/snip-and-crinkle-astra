"""Vertical transformation Short (1080x1920, ~18 s): "Oops! The Splash Becomes a Whale!"

Plan: reviews/pilot02_whale_short_plan.md. A second Short cut from the approved pilot, built on the benchmark's
strongest Shorts pattern (one satisfying transformation): the camera stays locked on the painting while it changes
from the friends picture to a splash, a dotted whale, seven painted layers and a before/after wipe.
Re-uses the vertical camera of pilot02_short.py (which loads the episode as S.E).

Run:  python3 episodes/pilot02_whale_short.py             (render -> output/pilot02_whale_short.mp4)
      python3 episodes/pilot02_whale_short.py --keys      (one frame per shot -> reviews/pilot02_whale_short_keys.png)
      python3 episodes/pilot02_whale_short.py --still T   (one full-size frame -> build/)
      python3 episodes/pilot02_whale_short.py --cuts      (cut times for check_video)
"""
import importlib.util
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "episodes"))

import hires  # noqa: E402

hires.set_res(2)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import music_extra as MX  # noqa: E402
from paperlib import ease_in_out, lerp, seg  # noqa: E402

_spec = importlib.util.spec_from_file_location("pilot02_short", os.path.join(ROOT, "episodes", "pilot02_short.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
E = S.E

OUT_W, OUT_H = S.OUT_W, S.OUT_H
CM = E.CANVAS_MID
CANV = (CM[0], CM[1] + 0.06 * OUT_H / 2.0, 2.0)          # locked canvas: centre at ~44% of the height
LAYER_ORDER = ("face", "tail", "spout", "waves", "boat", "bubbles", "rainbow")
WIPE = (0.5, 1.4)                                         # wipe runs between these local times of the wipe shot

# (source start, source end, framing) or ("wipe", duration, framing, source before, source after)
SEGS = [
    (24.0, 25.7, S.frame(1000, 1150, 1.3)),               # 1 trip, SPLAT
    (29.0, 30.6, CANV),                                   # 2 the ruined picture
    (36.2, 37.4, S.frame(1170, S.FY_CR, 1.8)),            # 3 uh-oh
    (66.4, 67.7, (1150, 1150, 2.0)),                      # 4 thinking... tap, boop: he paints his own nose
    (71.9, 72.8, (1150, 1100, 1.5)),                      # 5 idea!
    (77.0, 79.9, CANV),                                   # 6 a whale!
    *[(E.LAYER_T[n] - 0.3, E.LAYER_T[n] + 0.5, CANV) for n in LAYER_ORDER],   # 7-13 one layer per cut
    ("wipe", 2.0, CANV, 30.6, 111.0),                     # 14 before -> after
    (113.8, 116.4, S.frame(800, 1100, 1.4)),              # 15 paw-bump
]
OUT = []
_t = 0.0
for sg in SEGS:
    d = sg[1] if sg[0] == "wipe" else sg[1] - sg[0]
    OUT.append((_t, _t + d, sg))
    _t += d
DUR = round(_t, 3)


def seg_at(t):
    for o0, o1, sg in OUT:
        if t < o1:
            return o0, o1, sg
    return OUT[-1]


def film(src, fr):
    """The world at source time `src`, framed by (cx, cy, zoom) for the vertical frame."""
    d = K.drawing_of(src)
    cx, cy, z = fr
    ox = int(min(max(cx - 540, 0), E.P.WORLD_W - 1080))
    f = E.render_world(d / K.DPS, d, S.VCam(ox), S._bg(ox))
    cw, ch = 1080 / z, 1920 / z
    x0 = min(max(cx - cw / 2, ox), ox + 1080 - cw)
    y0 = min(max(cy - ch / 2, 0), 1920 - ch)
    box = ((x0 - ox) * S.RES, y0 * S.RES, (x0 - ox + cw) * S.RES, (y0 + ch) * S.RES)
    return f.resize((OUT_W, OUT_H), Image.LANCZOS, box=box).convert("RGB")


def _star(d, x, y, r, fill):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def wipe_frame(t_loc, fr, s_before, s_after):
    """Before on the right, after on the left of a sparkling line that sweeps left to right."""
    k = ease_in_out(seg(t_loc, *WIPE))
    before, after = film(s_before, fr), film(s_after, fr)
    gray = before.convert("L").convert("RGB")
    before = Image.blend(Image.blend(before, gray, 0.45), Image.new("RGB", before.size, (40, 36, 52)), 0.22)
    if k <= 0:
        return before
    if k >= 1:
        return after
    x = int(k * OUT_W)
    out = before.copy()
    out.paste(after.crop((0, 0, x, OUT_H)), (0, 0))
    glow = Image.new("L", (OUT_W, OUT_H), 0)
    ImageDraw.Draw(glow).rectangle([x - 14, 0, x + 14, OUT_H], fill=200)
    glow = glow.filter(ImageFilter.GaussianBlur(16))
    out.paste(Image.new("RGB", (OUT_W, OUT_H), (255, 252, 236)), (0, 0), glow)
    d = ImageDraw.Draw(out)
    d.rectangle([x - 4, 0, x + 4, OUT_H], fill=(255, 255, 250))
    for i, (yy, r) in enumerate(((560, 34), (840, 46), (1130, 30), (1380, 40))):
        wob = 1 + 0.25 * math.sin(2 * math.pi * (3 * t_loc + i * 0.3))
        _star(d, x, yy, r * wob, (255, 236, 140) if i % 2 else (255, 255, 255))
    return out


def render_frame(t, view="vert"):
    t_out = K.drawing_of(t) / K.DPS
    o0, o1, sg = seg_at(t_out)
    if sg[0] == "wipe":
        _, _, fr, s_before, s_after = sg
        return wipe_frame(t_out - o0, fr, s_before, s_after)
    s0, s1, fr = sg
    return film(min(s1 - 1e-3, s0 + (t_out - o0)), fr)


# ---------------------------------------------------------------- sound
def out_time(src_t):
    for o0, o1, sg in OUT:
        if sg[0] != "wipe" and sg[0] <= src_t < sg[1]:
            return o0 + (src_t - sg[0])
    return None


def build_audio(path):
    M = A.midi
    SR = A.SR
    _, sfx_ep = E.make_buses()
    sfx = np.zeros(int((DUR + 1) * SR))
    fade = int(0.008 * SR)
    for o0, o1, sg in OUT:
        if sg[0] == "wipe":
            continue
        piece = sfx_ep.buf[int(sg[0] * SR):int(sg[1] * SR)].copy()
        piece[:fade] *= np.linspace(0, 1, fade)
        piece[-fade:] *= np.linspace(1, 0, fade)
        i = int(o0 * SR)
        sfx[i:i + len(piece)] += piece
    o = [x[0] for x in OUT] + [DUR]                        # output start of each shot
    iw = next(i for i, x in enumerate(OUT) if x[2][0] == "wipe")
    w0 = o[iw]
    extra = A.Mix(DUR + 1)
    extra.add(w0, A.whoosh(0.45, 0.6)[::-1].copy())        # a little "rewind" back to the ruined picture
    extra.add(w0 + WIPE[0], A.whoosh(0.8, 0.8))
    extra.add(w0 + WIPE[0] + 0.2, A.chime_up(0.8))
    extra.add(w0 + WIPE[1] - 0.1, A.twinkle(0.7))
    sfx = sfx + extra.buf[:len(sfx)] * max(1e-9, abs(sfx).max()) / max(1e-9, abs(extra.buf).max())

    music = A.Mix(DUR)
    beat = 0.6

    def groove(t0, t1, chords, vel=0.34, inst=A.marimba, bass=True, shaker=True):
        t, i = t0, 0
        while t < t1 - 0.05:
            ch, root = chords[i % len(chords)]
            notes = MX.CHORDS[ch]
            for b in range(4):
                if t + b * beat / 2 < t1:
                    music.add(t + b * beat / 2, inst(M(notes[b % 4]), 0.5, vel if b % 2 == 0 else vel * 0.7))
                    if shaker:
                        music.add(t + b * beat / 2, A.shaker(0.28))
            if bass:
                music.add(t, A.bass(M(root), 0.5, 0.55))
            t += 2 * beat
            i += 1

    def pads(t0, t1, chords, vel=0.42):
        step = (t1 - t0) / len(chords)
        for i, ch in enumerate(chords):
            music.add(t0 + i * step, A.pad([M(m) for m in ch], step + 0.4, vel))

    A.jingle(music, 0.0, 0.7)
    pads(o[1], o[3], [(57, 60, 64), (53, 57, 60)], 0.45)                          # 2-3 oh no
    groove(o[3], o[5], [("C", 48), ("G", 43)], vel=0.28, inst=MX.toy_piano, bass=False)   # 4-5 boop, idea
    groove(o[5], w0, [("C", 48), ("F", 41), ("G", 43), ("C", 48)], vel=0.3)       # 6-13 painting
    pads(w0, o[iw + 1], [(48, 55, 64, 67), (53, 57, 65, 69)], 0.5)                # 14 before -> after
    for i, m in enumerate((72, 76, 79, 84)):
        music.add(w0 + WIPE[0] + i * 0.3, MX.melodica(M(m), 0.4, 0.3))
    groove(o[iw + 1], DUR, [("C", 48), ("F", 41), ("G", 43)], vel=0.34)          # 15 finale
    t_bump = out_time(E.T_PAWS)
    if t_bump is not None:
        A.jingle(music, t_bump + 0.02, 1.0, ending=True)
    music.add(DUR - 1.2, A.pad([M(48), M(55), M(64), M(72)], 1.6, 0.35))
    m = A.reverb(music.normalized(), 0.22)
    s = A.reverb(sfx[:int((DUR + 1) * SR)] / max(1e-9, abs(sfx).max()), 0.08)
    nm = lambda x: x / max(1e-9, abs(x).max())  # noqa: E731
    n = min(len(m), len(s))
    y = 0.45 * nm(m[:n]) + 0.7 * nm(s[:n])
    A.write_wav(path, y[:int(DUR * SR)] / max(1.0, abs(y).max() / 0.95), fade_out=0.25)


# ---------------------------------------------------------------- output
def key_sheet(path, w=270):
    import paperlib
    h = int(w * 1920 / 1080)
    cols = 8
    times = [o0 + 0.6 * (o1 - o0) for o0, o1, _ in OUT]
    iw = next(i for i, x in enumerate(OUT) if x[2][0] == "wipe")
    times.insert(iw + 1, OUT[iw][0] + 0.95)               # the wipe half-way
    rows = math.ceil(len(times) / cols)
    sheet = Image.new("RGB", (w * cols + 6 * (cols + 1), (h + 30) * rows + 6), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    font = paperlib.round_font(17)
    for i, tt in enumerate(times):
        im = render_frame(tt).convert("RGB").resize((w, h), Image.LANCZOS)
        x = 6 + (i % cols) * (w + 6)
        y = 6 + (i // cols) * (h + 30)
        d.text((x + 3, y + 3), f"{i + 1}  {tt:.1f}s", fill=(60, 50, 70), font=font)
        sheet.paste(im, (x, y + 24))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    if "--keys" in sys.argv:
        key_sheet(os.path.join(ROOT, "reviews", "pilot02_whale_short_keys.png"))
    elif "--cuts" in sys.argv:
        print(",".join(f"{o0:.2f}" for o0, *_ in OUT[1:]))
    elif "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(ROOT, "build", f"pilot02_whale_short_{tt:.2f}.png")
        render_frame(tt).convert("RGB").save(out)
        print("wrote", out)
    else:
        wav = os.path.join(ROOT, "build", "pilot02_whale_short_audio.wav")
        build_audio(wav)
        print("duration", DUR)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "pilot02_whale_short.mp4"), wav, DUR,
                       "vert")
