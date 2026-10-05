"""Vertical Short (1080x1920, ~43 s): a re-cut of the approved pilot "Oops! A Splash of Blue".

Plan: reviews/pilot02_short_plan.md. The episode's performances are re-filmed through a vertical camera
(each shot picks a moment of the episode and frames it for a phone). Sound: the episode's effects are cut
with the pictures; the music is a new continuous bed composed for the Short's own timeline.

Run:  python3 episodes/pilot02_short.py             (render -> output/pilot02_short.mp4)
      python3 episodes/pilot02_short.py --keys      (one frame per shot -> reviews/pilot02_short_keys.png)
      python3 episodes/pilot02_short.py --still T   (one full-size frame -> build/)
      python3 episodes/pilot02_short.py --cuts      (cut times for check_video)
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
from PIL import Image, ImageDraw  # noqa: E402

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import music_extra as MX  # noqa: E402
import props_artcorner as P  # noqa: E402
from paperlib import ease_in_out, lerp, seg  # noqa: E402

_spec = importlib.util.spec_from_file_location("pilot02_episode",
                                               os.path.join(ROOT, "episodes", "pilot02_splash_of_blue.py"))
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

RES = hires.RES
OUT_W, OUT_H = 1080, 1920
WORLD_BG = P.background()
FY_SN, FY_CR = 1119, 1066                      # face heights (world) of Snip and Crinkle


def frame(cx, face_y, z):
    """Framing that puts faces at about 40% of the height."""
    return cx, face_y + 0.1 * OUT_H / z, z


cv = E.cv
CM = E.CANVAS_MID
# (source start, source end, (cx, cy, zoom) or (cx, cy, zoom_from, zoom_to))
SEGS = [
    (1.0, 3.4, frame(640, 1100, 1.45)),            # 1 Snip paints
    (10.4, 11.5, frame(440, FY_SN, 1.8)),          # 2 something's missing
    (12.3, 13.4, (1590, 1290, 2.0)),               # 3 the blue jar
    (19.2, 20.4, frame(1540, FY_CR, 1.5)),         # 4 picks it up
    (21.0, 22.7, frame(1350, FY_CR, 1.5)),         # 5 carries it
    (22.7, 24.2, (1250, 1400, 2.0)),               # 6 the block
    (24.2, 25.9, frame(1000, 1150, 1.3)),          # 7 trip, SPLAT
    (29.0, 30.6, (CM[0], CM[1], 2.0)),             # 8 the ruined picture
    (31.3, 33.9, frame(420, FY_SN, 1.8)),          # 9 Snip: shock, sad
    (36.0, 37.6, frame(1170, FY_CR, 1.8)),         # 10 Crinkle: uh-oh
    (46.4, 49.9, (1146, 1047, 1.1)),               # 11 the thought: sneak away or sorry?
    (52.6, 54.8, frame(655, 1100, 1.29)),          # 12 sorry
    (55.4, 57.9, frame(685, 1100, 1.4)),           # 13 hug
    (66.4, 67.7, (1150, 1150, 2.0)),               # 14 boop: blue nose
    (68.3, 69.1, frame(475, FY_SN, 2.0)),          # 15 Snip giggles
    (69.5, 70.8, frame(1150, FY_CR, 1.55)),        # 16 Crinkle sees it, laughs (wider: the laugh bounces)
    (71.9, 72.8, (1150, 1100, 1.5)),               # 17 idea!
    (77.4, 79.9, (CM[0], CM[1], 2.0)),             # 18 a whale!
    (83.9, 84.8, (*cv(112, 168), 2.0)),            # 19 eye
    (87.7, 88.6, (*cv(270, 130), 2.0)),            #    tail
    (92.9, 93.8, (*cv(130, 100), 2.0)),            #    spout
    (96.1, 97.0, (*cv(200, 250), 2.0)),            #    waves
    (98.5, 99.4, (*cv(80, 240), 2.0)),             #    boat
    (102.1, 103.0, (*cv(200, 110), 2.0)),          #    rainbow
    (104.8, 108.8, (CM[0], 1180, 1.15, 2.0)),      # 20 the reveal (push in)
    (113.8, 116.4, frame(800, 1100, 1.4)),         # 21 paw-bump
]
OUT = []
_t = 0.0
for s0, s1, fr in SEGS:
    OUT.append((_t, _t + (s1 - s0), s0, s1, fr))
    _t += s1 - s0
DUR = round(_t, 3)


def seg_at(t):
    for o0, o1, s0, s1, fr in OUT:
        if t < o1:
            return o0, o1, s0, s1, fr
    return OUT[-1]


class VCam:
    def __init__(self, ox):
        self.ox, self.oy, self.res = ox, 0, RES

    def S(self, p):
        return (p[0] - self.ox) * self.res, (p[1] - self.oy) * self.res


_BG = {}


def _bg(ox):
    if ox not in _BG:
        _BG[ox] = WORLD_BG.crop((int(ox * RES), 0, int((ox + 1080) * RES), int(1920 * RES)))
    return _BG[ox]


def render_frame(t, view="vert"):
    t_out = K.drawing_of(t) / K.DPS
    o0, o1, s0, s1, fr = seg_at(t_out)
    src = min(s1 - 1e-3, s0 + (t_out - o0))
    d = K.drawing_of(src)
    tq = d / K.DPS
    if len(fr) == 4:
        cx, cy, z0, z1 = fr
        z = lerp(z0, z1, ease_in_out(seg(t_out, o0 + 0.3, o1)))
    else:
        cx, cy, z = fr
    ox = int(min(max(cx - 540, 0), P.WORLD_W - 1080))
    f = E.render_world(tq, d, VCam(ox), _bg(ox))
    cw, ch = 1080 / z, 1920 / z
    x0 = min(max(cx - cw / 2, ox), ox + 1080 - cw)
    y0 = min(max(cy - ch / 2, 0), 1920 - ch)
    box = ((x0 - ox) * RES, y0 * RES, (x0 - ox + cw) * RES, (y0 + ch) * RES)
    return f.resize((OUT_W, OUT_H), Image.LANCZOS, box=box)


# ---------------------------------------------------------------- sound
def out_time(src_t):
    for o0, o1, s0, s1, fr in OUT:
        if s0 <= src_t < s1:
            return o0 + (src_t - s0)
    return None


def build_audio(path):
    M = A.midi
    SR = A.SR
    _, sfx_ep = E.make_buses()
    sfx = np.zeros(int((DUR + 1) * SR))
    fade = int(0.008 * SR)
    for o0, o1, s0, s1, fr in OUT:
        piece = sfx_ep.buf[int(s0 * SR):int(s1 * SR)].copy()
        piece[:fade] *= np.linspace(0, 1, fade)
        piece[-fade:] *= np.linspace(1, 0, fade)
        i = int(o0 * SR)
        sfx[i:i + len(piece)] += piece
    music = A.Mix(DUR)
    beat = 0.6

    def groove(t0, t1, chords, vel=0.36, inst=A.marimba, bass=True, shaker=True):
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
        n = len(chords)
        step = (t1 - t0) / n
        for i, ch in enumerate(chords):
            music.add(t0 + i * step, A.pad([M(m) for m in ch], step + 0.4, vel))

    o = [x[0] for x in OUT] + [DUR]                        # output start of each shot
    I_IV = [("C", 48), ("F", 41), ("C", 48), ("G", 43)]
    A.jingle(music, 0.0, 0.9)
    groove(0.6, o[5], I_IV)                                # 1-5 happy
    pads(o[5], o[6], [(50, 55, 62)], 0.35)                 # 6 suspense
    pads(o[6], o[10], [(57, 60, 64), (53, 57, 60), (57, 60, 64)], 0.45)   # 7-10 oh no
    pads(o[10], o[11], [(50, 57, 62), (55, 59, 62)], 0.4)  # 11 the choice
    pads(o[11], o[12], [(48, 55, 64)], 0.4)                # 12 sorry
    for tt, m, dd in ((o[11] + 0.3, 72, 0.45), (o[11] + 0.8, 71, 0.45), (o[11] + 1.3, 67, 0.8)):
        music.add(tt, MX.melodica(M(m), dd, 0.3))
    groove(o[12], o[13], [("F", 41), ("C", 48)], vel=0.3, shaker=False)   # 13 hug
    for tt, m, dd in ((o[12] + 0.6, 72, 0.5), (o[12] + 1.2, 76, 0.5), (o[12] + 1.8, 79, 0.7)):
        music.add(tt, MX.melodica(M(m), dd, 0.3))
    groove(o[13], o[17], [("C", 48), ("G", 43), ("F", 41), ("C", 48)], vel=0.32, inst=MX.toy_piano)  # 14-17 giggles
    groove(o[17], o[24], [("C", 48), ("F", 41), ("G", 43), ("C", 48)], vel=0.3)                     # 18-19 painting
    pads(o[24], o[25], [(48, 55, 64, 67), (53, 57, 65, 69)], 0.5)                                    # 20 the reveal
    for i, m in enumerate((72, 76, 79, 84, 79, 76, 77, 81)):
        music.add(o[24] + 0.2 + i * 0.48, MX.melodica(M(m), 0.42, 0.3))
    groove(o[25], DUR, [("C", 48), ("F", 41), ("G", 43)], vel=0.34)                                 # 21 finale
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
    cols = 9
    times = [o0 + 0.6 * (o1 - o0) for o0, o1, *_ in OUT]
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
        key_sheet(os.path.join(ROOT, "reviews", "pilot02_short_keys.png"))
    elif "--cuts" in sys.argv:
        print(",".join(f"{o0:.2f}" for o0, *_ in OUT[1:]))
    elif "--still" in sys.argv:
        tt = float(sys.argv[sys.argv.index("--still") + 1])
        out = os.path.join(ROOT, "build", f"pilot02_short_{tt:.2f}.png")
        render_frame(tt).convert("RGB").save(out)
        print("wrote", out)
    else:
        wav = os.path.join(ROOT, "build", "pilot02_short_audio.wav")
        build_audio(wav)
        print("duration", DUR)
        K.render_video(os.path.abspath(__file__), os.path.join(ROOT, "output", "pilot02_short.mp4"), wav, DUR, "vert")
