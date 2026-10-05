"""Acting kit for long-form episodes (first used by the pilot).

What it adds on top of characters.Character (which stays untouched, so Episodes 1-10 render
exactly as before):
  * faces with eyebrows (calm / up / sad / sorry / worry / focus), extra mouths (frown, talk, hum,
    oo, smile_open) and "glassy" eyes for big feelings;
  * Perf: a performance timeline. Moves between poses with anticipation ("antic"), overshoot
    ("back") or both ("snap"); facial changes on exact times; lip-sync from voices.Line; automatic
    blinks, breathing and ear sway; Snip's ear moods (ears show feelings);
  * paper "boil": tiny per-drawing wobble so the puppets feel handmade;
  * Cam: one world, two views (1920x1080 landscape for long-form, 1080x1920 vertical for Shorts);
  * drawing on twos (15 drawings a second, each shown twice at 30 fps) and a parallel renderer.

    import acting as K
    snip = K.Perf(K.Actor("snip", 0.95), x=600, y=FLOOR)
    snip.to(2.0, 2.4, "snap", arm_r=60, lean=-6)       # wind up, move, overshoot, settle
    snip.face(2.0, eyes="wide", brows="up")
    snip.ears(2.0, 2.5, "droop")
    snip.say(2.6, V.snip("aww"))
    snip.draw(frame, t, cam, drawing)
"""
import math
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from characters import (CRINKLE, EYE, MOUTH_DARK, SNIP, SNIP_FACE_PIVOT, TONGUE,  # noqa: E402
                        Character, _eyes, _mouth)
from paperlib import Cut, clamp01, ease_out_back, place  # noqa: E402

DPS = 15                              # drawings per second ("on twos" at 30 fps)
FPS = 30
TEAR = (150, 206, 246)


# ---------------------------------------------------------------- faces
BROWS = {   # lift (in eye heights), inner-end rise (fraction of length), arch
    "calm": (0.0, -0.04, 0.10), "up": (0.55, 0.02, 0.22), "sad": (0.12, 0.34, 0.02),
    "sorry": (0.0, 0.40, 0.0), "worry": (0.22, 0.26, 0.06), "focus": (-0.18, -0.24, 0.04),
}


def _brows(c, pts, kind, r, look):
    if not kind or kind == "none":
        return
    rx, ry = r
    lift, rise, arch = BROWS[kind]
    L = rx * 2.3
    for i, (x, y) in enumerate(pts):
        d = 1 if i == 0 else -1                    # direction from outer end to inner end
        cx, cy = x + look[0] * 0.35, y - ry * (1.75 + lift) + look[1] * 0.25
        outer = (cx - d * L / 2, cy + rise * L / 2)
        inner = (cx + d * L / 2, cy - rise * L / 2)
        mid = (cx, cy - arch * L)
        c.line([outer, mid, inner], rx * 0.42, EYE)


def _eyes2(c, pts, kind, r, look):
    if kind != "glassy":
        return _eyes(c, pts, kind, r, look)
    rx, ry = r
    for x, y in pts:
        ex, ey = x + look[0], y + look[1]
        c.ellipse(ex, ey, rx * 1.18, ry * 1.15, EYE, sil=False)
        c.ellipse(ex + rx * 0.4, ey - ry * 0.42, rx * 0.46, rx * 0.46, (255, 255, 255), sil=False)
        c.ellipse(ex - rx * 0.42, ey + ry * 0.2, rx * 0.26, rx * 0.26, (255, 255, 255), sil=False)
        c.arc(ex, ey + ry * 0.2, rx * 1.25, ry * 1.05, 30, 150, rx * 0.3, TEAR)   # wet lower lid


def _mouth2(c, cx, my, kind, k=1.0):
    if kind == "frown":
        c.arc(cx, my + 16 * k, 20 * k, 13 * k, 205, 335, 5 * k, EYE)
    elif kind == "talk":
        c.ellipse(cx, my + 6 * k, 13 * k, 10 * k, MOUTH_DARK, sil=False)
        c.chord(cx, my + 11 * k, 8 * k, 5 * k, 180, 360, TONGUE)
    elif kind == "hum":
        c.arc(cx, my + 2 * k, 11 * k, 6 * k, 20, 160, 4.5 * k, EYE)
    elif kind == "oo":
        c.ellipse(cx, my + 6 * k, 7 * k, 8 * k, MOUTH_DARK, sil=False)
    elif kind == "smile_open":
        c.chord(cx, my - 2 * k, 20 * k, 18 * k, 0, 180, MOUTH_DARK)
        c.chord(cx, my + 11 * k, 11 * k, 6 * k, 180, 360, TONGUE)
    else:
        _mouth(c, cx, my, kind, k)


def snip_face2(eyes="normal", mouth="w", look=(0, 0), brows="calm"):
    c = Cut(300, 290)
    c.ellipse(150, 150, 140, 122, SNIP["fur"])
    puff = mouth == "blow"
    for x in (76, 224):
        c.ellipse(x, 186, 27 if puff else 22, 17 if puff else 13, SNIP["cheek"], sil=False)
    eye_pts = [(103, 138), (197, 138)]
    _eyes2(c, eye_pts, eyes, (15, 20), look)
    _brows(c, eye_pts, brows, (15, 20), look)
    c.ellipse(150, 170, 13, 9, SNIP["nose"], sil=False)
    _mouth2(c, 150, 186, mouth)
    return c.finish(pivot=SNIP_FACE_PIVOT)


def crinkle_head2(eyes="normal", mouth="smile", look=(0, 0), brows="calm"):
    c = Cut(340, 330)
    fur = CRINKLE["fur"]
    for x in (70, 270):
        c.ellipse(x, 74, 56, 56, fur)
        c.ellipse(x, 78, 31, 31, CRINKLE["ear_in"], sil=False)
    c.ellipse(170, 190, 160, 128, fur)
    c.ellipse(170, 240, 74, 54, CRINKLE["muzzle"], sil=False)
    puff = mouth == "blow"
    for x in (78, 262):
        c.ellipse(x, 224, 30 if puff else 22, 19 if puff else 13, CRINKLE["cheek"], sil=False)
    eye_pts = [(110, 170), (230, 170)]
    _eyes2(c, eye_pts, eyes, (16, 21), look)
    _brows(c, eye_pts, brows, (16, 21), look)
    c.ellipse(170, 216, 27, 18, CRINKLE["nose"], sil=False)
    c.ellipse(161, 211, 8, 4, (140, 104, 88), sil=False)
    _mouth2(c, 170, 250, mouth, 1.1)
    return c.finish(pivot=(170, 312))


BLINKABLE = ("normal", "wide", "sparkle", "glassy")


class Actor(Character):
    """A Character whose faces also carry eyebrows and the extra mouths/eyes above."""

    def __init__(self, kind, scale=1.0):
        super().__init__(kind, scale)
        self._face = snip_face2 if kind == "snip" else crinkle_head2
        self._brow = "calm"

    def head(self, eyes, mouth, look):
        key = (eyes, mouth, look, self._brow)
        if key not in self._heads:
            self._heads[key] = self._face(eyes, mouth, look, self._brow).scaled(self.s)
        return self._heads[key]


# ---------------------------------------------------------------- easing
def _smooth(p):
    return p * p * (3 - 2 * p)


def _in_back(p, s=1.9):
    return p * p * ((s + 1) * p - s)


def _in_out_back(p, s=1.7 * 1.525):
    p2 = p * 2
    if p2 < 1:
        return 0.5 * (p2 * p2 * ((s + 1) * p2 - s))
    p2 -= 2
    return 0.5 * (p2 * p2 * ((s + 1) * p2 + s) + 2)


EASES = {
    "lin": lambda p: p,
    "io": _smooth,
    "out": lambda p: 1 - (1 - p) ** 3,
    "in": lambda p: p ** 3,
    "back": ease_out_back,                     # overshoot, then settle
    "antic": _in_back,                         # wind up the other way first
    "snap": _in_out_back,                      # wind up, move, overshoot, settle
    "step": lambda p: 1.0 if p >= 1 else 0.0,
}


# ---------------------------------------------------------------- performance
NUM = ("x", "y", "hop", "lean", "tilt", "arm_l", "arm_r", "head_dy", "sq", "ear_l", "ear_r", "ear_k",
       "look_x", "look_y", "alpha", "frizz")
TXT = ("eyes", "mouth", "brows")

EAR_MOODS = {   # Snip's ears show feelings: (left extra, right extra, stretch)
    "up": (0, 0, 1.0), "perk": (-7, 7, 1.08), "alarm": (-12, 12, 1.16), "curious": (0, -36, 1.0),
    "sad": (42, -42, 0.95), "droop": (70, -70, 0.9), "shy": (24, -10, 0.96), "happy": (-4, 4, 1.04),
}


class Perf:
    """One character's performance: a timeline of moves, faces, voice lines and hops."""

    def __init__(self, actor, seed=0, **init):
        self.a = actor
        rest_l = -14.0
        self.init = dict(x=0.0, y=0.0, hop=0.0, lean=0.0, tilt=0.0, arm_l=rest_l, arm_r=14.0, head_dy=0.0,
                         sq=1.0, ear_l=0.0, ear_r=0.0, ear_k=1.0, look_x=0.0, look_y=0.0, alpha=1.0, frizz=0.0,
                         eyes=actor._default[0], mouth=actor._default[1], brows="calm")
        self.init.update(init)
        self.moves = {c: [] for c in NUM}
        self.steps = {c: [] for c in TXT}
        self.lines, self.hops, self.wiggles = [], [], []
        self.seed = seed
        self.blinks = self._auto_blinks(seed)
        self.no_blink = []
        self.mouth_lock = []          # spans where talking does not take over the mouth
        self.arms_front = []          # spans where the arms are drawn over the head (paws on cheeks)

    # --- authoring
    def to(self, t0, t1, ease="io", **vals):
        for c, v in vals.items():
            if c in TXT:
                self.steps[c].append((t0, v))
            else:
                self.moves[c].append((t0, t1, float(v), ease))
        return self

    def set(self, t, **vals):
        return self.to(t, t, "step", **vals)

    def face(self, t, **vals):
        for c, v in vals.items():
            self.steps[c].append((t, v))
        return self

    def ears(self, t0, t1, mood, ease="back"):
        l, r, k = EAR_MOODS[mood]
        return self.to(t0, t1, ease, ear_l=l, ear_r=r, ear_k=k)

    def say(self, t, line):
        self.lines.append((t, line))
        return self

    def hop(self, t0, t1, n=1, height=40):
        self.hops.append((t0, t1, n, height))
        return self

    def wiggle(self, t0, chan, amp, freq=5.0, damp=4.5):
        """Damped spring on a channel from t0 (ear flick, head shake, wobble)."""
        self.wiggles.append((t0, chan, amp, freq, damp))
        return self

    def blink(self, *times):
        self.blinks.extend(times)
        return self

    # --- evaluation
    @staticmethod
    def _auto_blinks(seed):
        r = np.random.default_rng(1000 + seed)
        t, out = 0.6 + r.uniform(0, 1.2), []
        while t < 600:
            out.append(t)
            t += r.uniform(2.2, 4.2)
        return out

    def _num(self, c, t):
        v = self.init[c]
        for t0, t1, tgt, ease in sorted(self.moves[c], key=lambda m: m[0]):
            if t >= t1:
                v = tgt
            elif t > t0:
                p = clamp01((t - t0) / (t1 - t0))
                v = v + (tgt - v) * EASES[ease](p)
                break
            else:
                break
        return v

    def _txt(self, c, t):
        v = self.init[c]
        for t0, val in sorted(self.steps[c], key=lambda s: s[0]):
            if t >= t0:
                v = val
            else:
                break
        return v

    def talk(self, t):
        return max([ln.level(t - t0) for t0, ln in self.lines if 0 <= t - t0 < ln.dur] or [0.0])

    def state(self, t, drawing=None):
        s = {c: self._num(c, t) for c in NUM}
        s.update({c: self._txt(c, t) for c in TXT})
        # hops with squash and stretch
        for t0, t1, n, hgt in self.hops:
            if t0 <= t < t1:
                q = ((t - t0) / (t1 - t0) * n) % 1.0
                air = math.sin(math.pi * q)
                s["hop"] += hgt * air
                s["sq"] *= 1 + 0.08 * air - 0.12 * (max(0, 1 - q / 0.12) + max(0, 1 - (1 - q) / 0.12))
            elif 0 <= t - t1 < 0.14:
                s["sq"] *= 1 - 0.1 * (1 - (t - t1) / 0.14)
        for t0, c, amp, freq, damp in self.wiggles:
            if t >= t0:
                dt = t - t0
                s[c] += amp * math.exp(-damp * dt) * math.sin(2 * math.pi * freq * dt)
        # life: breathing, ear sway
        s["sq"] *= 1 + 0.012 * math.sin(2 * math.pi * t / 2.4 + self.seed)
        sway = 2.0 * math.sin(2 * math.pi * t / 3.0 + self.seed)
        s["ear_l"] += sway
        s["ear_r"] -= sway
        # lip-sync
        lv = self.talk(t)
        locked = any(a <= t < b for a, b in self.mouth_lock)
        if lv > 0.08 and not locked:
            if self.a.kind == "snip":
                s["mouth"] = "oo" if lv < 0.55 else "o"
            else:
                s["mouth"] = "hum" if lv < 0.35 else ("talk" if lv < 0.75 else "O")
            s["tilt"] += 2.0 * lv * math.sin(2 * math.pi * t * 3.0)
            s["head_dy"] -= 3.0 * lv
        # blinks
        if s["eyes"] in BLINKABLE and not any(a <= t < b for a, b in self.no_blink):
            if any(0 <= t - b < 0.13 for b in self.blinks):
                s["eyes"] = "blink"
        # paper boil: a tiny different wobble on every drawing
        if drawing is not None:
            r = np.random.default_rng(drawing * 7919 + self.seed * 31 + 5)
            j = r.uniform(-1, 1, 4)
            s["lean"] += 0.25 * j[0]
            s["tilt"] += 0.45 * j[1]
            s["arm_l"] += 0.8 * j[2]
            s["arm_r"] += 0.8 * j[3]
        return s

    def draw(self, base, t, cam, drawing=None, st=None):
        s = st or self.state(t, drawing)
        self.a._brow = s["brows"]
        look = (int(round(s["look_x"] / 2) * 2), int(round(s["look_y"] / 2) * 2))
        self.a.draw(base, s["x"] - cam.ox, s["y"] - cam.oy, hop=s["hop"], lean=s["lean"], head_tilt=s["tilt"],
                    arm_l=s["arm_l"], arm_r=s["arm_r"], eyes=s["eyes"], mouth=s["mouth"], look=look,
                    alpha=s["alpha"], squash=s["sq"], head_dy=s["head_dy"], blink=False,
                    ears=(s["ear_l"], s["ear_r"]), ear_stretch=s["ear_k"], frizz=s["frizz"])
        if any(a <= t < b for a, b in self.arms_front):
            for side, spr, ang in (("l", self.a.arm_l, s["arm_l"]), ("r", self.a.arm_r, s["arm_r"])):
                sx, sy = self.a.shoulder_pt(s["x"], s["y"], side, s["hop"], s["lean"], s["sq"])
                place(base, spr, (sx - cam.ox, sy - cam.oy), angle=ang + s["lean"], alpha=s["alpha"])
        return s

    # helpers for props held in paws
    def paw(self, t, side, cam=None, st=None):
        s = st or self.state(t)
        arm = s["arm_l"] if side == "l" else s["arm_r"]
        x, y = self.a.paw_tip(s["x"], s["y"], side, arm, s["hop"], s["lean"], s["sq"])
        return (x - cam.ox, y - cam.oy) if cam else (x, y)


# ---------------------------------------------------------------- camera
class Cam:
    """A view into the world. `view` is "land" (1920x1080) or "vert" (1080x1920)."""

    def __init__(self, view, world_w, world_h, land_y0, vert_x0):
        self.view = view
        if view == "land":
            self.w, self.h, self.ox, self.oy = 1920, 1080, 0, land_y0
        else:
            self.w, self.h, self.ox, self.oy = 1080, 1920, vert_x0, 0
        self.world = (world_w, world_h)

    def crop_bg(self, bg):
        return bg.crop((self.ox, self.oy, self.ox + self.w, self.oy + self.h))

    def S(self, p):
        """World point -> screen point."""
        return p[0] - self.ox, p[1] - self.oy


def zoom(img, k, focus):
    """Push in by k (>= 1) towards a screen point, keeping the frame size."""
    if k <= 1.0001:
        return img
    from PIL import Image
    w, h = img.size
    cw, ch = w / k, h / k
    x0 = min(max(focus[0] - cw / 2, 0), w - cw)
    y0 = min(max(focus[1] - ch / 2, 0), h - ch)
    return img.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))


def drawing_of(t):
    """Index of the drawing shown at time t (15 a second)."""
    return int(math.floor(t * DPS + 1e-6))


# ---------------------------------------------------------------- parallel renderer
_EP = None
_VIEW = None


def _init(ep_path, view):
    global _EP, _VIEW
    import importlib.util
    mod = sys.modules.get("__mp_main__")
    if mod is None or not hasattr(mod, "render_frame"):
        spec = importlib.util.spec_from_file_location("episode_mod", ep_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    _EP, _VIEW = mod, view


def _draw(i):
    return _EP.render_frame(i / DPS, _VIEW).convert("RGB").tobytes()


def render_video(ep_path, out, wav, dur, view, workers=8):
    """Render drawing i at t = i/15 in parallel; write each one twice into a 30 fps MP4."""
    import multiprocessing as mp
    size = (1920, 1080) if view == "land" else (1080, 1920)
    n = int(round(dur * DPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, initializer=_init, initargs=(ep_path, view)) as pool:
        step = workers * 4
        for b in range(0, n, step):
            for frame in pool.map(_draw, range(b, min(n, b + step))):
                for _ in range(FPS // DPS):
                    proc.stdin.write(frame)
            print(f"drawing {min(n, b + step)}/{n}  {time.time() - t0:.0f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out, f"in {time.time() - t0:.0f}s")
    return out
