"""A2 rig test (COMEDY_PLAYBOOK section 9): eyes-only stills and two short gag clips, no episode.

    python3 episodes/rigtest_acting.py --stills          eyes-only test: 5 eye states x 2 friends, mouth hidden
                                                         -> build/rig_a2/<who>_<state>.png + eyes_only_sheet.png
    python3 episodes/rigtest_acting.py --strip           every-drawing strips of both gags -> build/rig_a2/strip_*.png
    python3 episodes/rigtest_acting.py --still T [clip]  one frame of a clip (snip | crinkle) -> build/rig_a2/
    python3 episodes/rigtest_acting.py --audio           both clips' sound -> build/rig_a2/rigtest_<clip>.wav
    python3 episodes/rigtest_acting.py --check           measured timing (take beats, sound 1 drawing after the
                                                         accent) and keysize lines
    RIG_CLIP=snip python3 episodes/rigtest_acting.py --render     -> output/rigtest_snip.mp4 (low-res, RES 1)

Gag (both clips, 4.6 s): a set-up (something drifts in; the friend hasn't seen it), a still pause, a notice dart
with a blink, a take (sees 0.2 s, squash 0.27 s, snap 2 drawings, hold 0.5 s, settle 0.3 s) and a delighted grin.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hires  # noqa: E402

STILLS = "--stills" in sys.argv
hires.set_res(float(os.environ.get("RIG_RES", "2" if STILLS else "1")))

import acting as K  # noqa: E402
import audio as A  # noqa: E402
import rig2 as R  # noqa: E402
from hires import RCut  # noqa: E402
from paperlib import place  # noqa: E402

RES = hires.RES
W, H, FLOOR = 1920, 1080, 1000
OUT = os.path.join(ROOT, "build", "rig_a2")
DUR = 4.6
STATES = ("neutral", "curious", "cross", "sad", "delighted")
SCALE = {"snip": 1.3, "crinkle": 1.2}
FOCUS = {"snip": ((960, 500), 1.5), "crinkle": ((960, 560), 1.6)}   # close-up centre (world) and zoom

# take beats (s): sees, squash, snap (2 drawings), hold 0.5, settle 0.3
T_DART, T_SQ, T_SNAP, T_EXT, T_SETTLE, T_GRIN = 1.8, 2.0, 2.27, 2.40, 2.90, 3.20
SOUND_HIT = T_EXT + 1 / K.DPS          # 1 drawing after the visual accent
T_POP = 2.0                            # Snip: the bubble pops on her nose (the take's visible cause)


def _bg():
    img = Image.new("RGBA", (int(W * RES), int(H * RES)), (246, 236, 214, 255))
    d = ImageDraw.Draw(img)
    for i in range(12):                                    # soft paper bands, a floor
        y0 = int(i * 80 * RES)
        d.rectangle([0, y0, img.width, y0 + int(40 * RES)], fill=(243, 232, 209, 255))
    d.rectangle([0, int(FLOOR * RES), img.width, img.height], fill=(214, 190, 160, 255))
    return img


def _bubble():
    c = RCut(190, 190)
    c.ellipse(95, 95, 82, 82, (176, 214, 244))
    c.ellipse(95, 95, 67, 67, (214, 234, 250), sil=False)
    c.ellipse(67, 64, 19, 15, (255, 255, 255), sil=False)
    return c.finish(pivot=(95 * RES, 95 * RES))


def _pop():
    c = RCut(240, 240)
    c.arc(120, 120, 72, 72, 0, 360, 9, (84, 156, 226))
    for i in range(8):
        a = math.radians(i * 45 + 20)
        c.ellipse(120 + 100 * math.cos(a), 120 + 100 * math.sin(a), 13, 13, (84, 156, 226), sil=False)
    return c.finish(pivot=(120 * RES, 120 * RES))


def _leaf(k=1.6):
    c = RCut(int(120 * k), int(90 * k))
    c.polygon([(x * k, y * k) for x, y in ((10, 45), (40, 15), (80, 12), (110, 45), (80, 78), (40, 75))], (226, 128, 52))
    c.line([(14 * k, 45 * k), (106 * k, 45 * k)], 4 * k, (160, 80, 30))
    return c.finish(pivot=(60 * k * RES, 45 * k * RES))


def performer(who, seed=1):
    p = R.Perf2(R.Puppet(who, SCALE[who]), seed=seed, x=960, y=FLOOR)
    p.acting(overlap=1.0, breath=True, ears=True, blink="soft", auto_blink=False)
    return p


# ---------------------------------------------------------------- the gag clips
def build_clip(who):
    p = performer(who, seed=2 if who == "snip" else 3)
    p.set(0, look_x=-6, look_y=0, mouth="none" if False else ("w" if who == "snip" else "smile"))
    p.blink(0.9)                                           # one thought blink in the set-up
    up = who == "crinkle"                                  # Crinkle notices a leaf on his head: looks up
    p.dart(T_DART, 4 if up else 12, -12 if up else -4)     # notice: a 2-frame dart, a quick blink (>= 10 units)
    if up:
        p.to(T_DART + 0.07, T_SQ, "out", tilt=-4)
    else:                                                  # her eyes follow the bubble onto her nose
        p.to(T_DART + 2 / K.FPS, T_POP, "io", look_x=3, look_y=5)
    # take: squash (eyes small), snap to the extreme, hold, settle
    p.to(T_SQ, T_SNAP, "io", sq=0.86, head_dy=10, lid=0.35, arm_l=-6, arm_r=6)
    p.face(T_SQ, mouth="flat")
    p.to(T_SNAP, T_EXT, "out", sq=1.12, head_dy=-8, lid=0.0, arm_l=-40, arm_r=40)
    p.face(T_SNAP + 1 / K.DPS, eyes="wide", brows="up", mouth="O")
    p.ears(T_SNAP, T_EXT, "alarm", ease="out")
    p.to(T_SETTLE, T_GRIN, "io", sq=1.0, head_dy=0)
    p.emote(T_SETTLE, T_GRIN, "delighted", body=False)
    p.to(T_SETTLE, T_GRIN, "io", tilt=-6 if not up else 6, arm_l=-26, arm_r=26)
    p.face(T_SETTLE + 0.1, mouth="smile_open" if who == "snip" else "grin")
    p.wiggle(T_GRIN, "tilt", 3.0, freq=3.0, damp=3.5)      # a little giggle shake
    return p


_CLIPS = {}


def clip(who):
    if who not in _CLIPS:
        _CLIPS[who] = build_clip(who)
    return _CLIPS[who]


def prop_pos(who, t, st, p):
    """World position and angle of the clip's cause (bubble beside Snip's head; leaf on Crinkle's head)."""
    if who == "snip":
        nose = p.a.face_point(st, (0, -90))
        rest, bob = (nose[0] + 300, nose[1] - 60), 10 * math.sin(2 * math.pi * t / 1.6)
        if t < 1.4:                                        # set-up: drifts in from the right
            e = 1 - (1 - t / 1.4) ** 2
            return (1900 + (rest[0] - 1900) * e, rest[1] + 120 * (1 - e) + bob), 0.0
        if t < T_DART:                                     # the pause: almost still
            return (rest[0], rest[1] + 0.4 * bob), 0.0
        if t < T_POP:                                      # she sees it come; it drifts onto her nose
            u = (t - T_DART) / (T_POP - T_DART)
            e = u * u * (3 - 2 * u)
            touch = (nose[0] + 66, nose[1] + 64)          # below-right: touches the nose, clear of the eye
            return (rest[0] + (touch[0] - rest[0]) * e, rest[1] + (touch[1] - rest[1]) * e), 0.0
        if t < T_POP + 2 / K.DPS:                          # pop: a ring and droplets for 2 drawings
            return (nose[0] + 66, nose[1] + 64), 0.0
        return None, 0.0
    top = p.a.face_point(st, (0, -264))
    if t < 1.4:                                            # falls, swaying, onto his head
        u = t / 1.4
        return (top[0] + 60 * math.sin(2 * math.pi * u * 1.5) * (1 - u), top[1] - 520 * (1 - u)), 25 * math.sin(6 * u)
    if t < T_EXT:
        return (top[0], top[1] - 10), st["tilt"]
    u = min(1.0, (t - T_EXT) / 1.4)                        # popped up by the snap, flutters down in front
    lift = 110 * math.sin(math.pi * min(1.0, u * 1.6)) if u < 0.62 else 110 * math.sin(math.pi * 0.992) - 0
    y = top[1] - 10 - lift + 330 * max(0.0, u - 0.5) * 2 + 260 * max(0.0, t - T_EXT - 1.4)   # on to the floor
    return (top[0] + 380 * u, min(FLOOR - 20, y)), 40 * math.sin(5 * u)


_SPR = {}


def render_clip(who, t, zoom=True):
    p = clip(who)
    d = K.drawing_of(t)
    img = _bg()
    cam = K.Cam("land", W, H, 0, 0, res=RES)
    st = p.draw(img, t, cam, d)
    if "bubble" not in _SPR:
        _SPR["bubble"], _SPR["leaf"], _SPR["pop"] = _bubble(), _leaf(), _pop()
    pos, ang = prop_pos(who, t, st, p)
    if pos is not None:
        spr = _SPR["leaf"] if who == "crinkle" else _SPR["pop" if t >= T_POP else "bubble"]
        place(img, spr, cam.S(pos), angle=ang)
    return _frame(img, who, zoom), st


def _frame(img, who, zoom=True):
    (fx, fy), z = FOCUS[who] if zoom else ((W / 2, H / 2), 1.0)
    z = min(z, 1.25) if not STILLS and zoom else z         # the clips: a medium close-up
    fy = fy - 50 if (not STILLS and zoom) else fy             # clips: room for the ears at the stretch
    cw, ch = W * RES / z, H * RES / z
    x0 = min(max(fx * RES - cw / 2, 0), W * RES - cw)
    y0 = min(max(fy * RES - ch / 2, 0), H * RES - ch)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def render_frame(t, view="land"):
    return render_clip(os.environ.get("RIG_CLIP", "snip"), t)[0]


# ---------------------------------------------------------------- eyes-only stills
def eyes_only():
    os.makedirs(OUT, exist_ok=True)
    cells = []
    for who in ("snip", "crinkle"):
        for name in STATES:
            p = performer(who)
            p.set(0, mouth="none")
            p.emote(0.0, 0.5, name)
            img = _bg()
            p.draw(img, 1.0, K.Cam("land", W, H, 0, 0, res=RES), K.drawing_of(1.0))
            out = _frame(img, who)
            path = os.path.join(OUT, f"{who}_{name}.png")
            out.convert("RGB").save(path)
            print("wrote", path)
            cells.append((who, name, out.crop((360, 0, 1560, 1080)).resize((400, 360), Image.LANCZOS)))
    sheet = Image.new("RGB", (2000, 2 * 390), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (who, name, im) in enumerate(cells):
        x, y = (i % 5) * 400, (i // 5) * 390
        sheet.paste(im.convert("RGB"), (x, y + 30))
        dr.text((x + 8, y + 8), f"{who} {name} (mouth hidden)", fill=(0, 0, 0))
    path = os.path.join(OUT, "eyes_only_sheet.png")
    sheet.save(path)
    print("wrote", path)


def strip(who):
    t0, t1 = 1.6, 3.4
    n = int(round((t1 - t0) * K.DPS))
    cols, tw = 9, 200
    sheet = Image.new("RGB", (cols * tw, ((n + cols - 1) // cols) * (tw + 22)), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    for i in range(n):
        t = t0 + i / K.DPS
        img, st = render_clip(who, t)
        th = img.crop((560, 60, 1360, 860)).resize((tw, tw), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (tw + 22)
        sheet.paste(th.convert("RGB"), (x, y + 22))
        dr.text((x + 4, y + 4), f"{t:.3f}s sq{st['sq']:.2f} {st['eyes'][:5]}", fill=(0, 0, 0))
    path = os.path.join(OUT, f"strip_{who}.png")
    sheet.save(path)
    print("wrote", path)


# ---------------------------------------------------------------- sound: cue, silence-ish pause, hit, giggles
def sound(who):
    m = A.Mix(DUR)
    for t, ch in ((0.0, (60, 64, 67)), (1.9, (60, 65, 69)), (2.9, (62, 67, 71))):
        m.add(t, A.pad([A.midi(n) for n in ch], 2.6, 1.0), 0.05)
    m.add(0.02, A.glock(A.midi(91), 0.8, 0.5), 0.3)       # cue: the cause arrives
    if who == "snip":                                      # soft plip, 1 drawing after the pop drawing
        m.add(T_POP + 1 / K.DPS, A.pop(0.6), 0.4)
        m.add(T_POP + 1 / K.DPS, A.glock(A.midi(100), 0.25, 0.6), 0.15)
    m.add(SOUND_HIT, A.boing(1.0, 300 if who == "snip" else 220), 0.9)   # the take's punctuation
    for i, n in enumerate((84, 88, 91, 88, 93)):           # giggle notes, never a voice
        m.add(T_GRIN + 0.08 * i, A.marimba(A.midi(n), 0.3, 0.8), 0.45)
    return m


def write_audio():
    os.makedirs(OUT, exist_ok=True)
    for who in ("crinkle", "snip"):
        path = os.path.join(OUT, f"rigtest_{who}.wav")
        A.write_wav(path, sound(who).normalized(0.7))
        print("wrote", path)


def _lufs(path):
    import re
    import subprocess
    r = subprocess.run(["ffmpeg", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


def trim_loudness(path, target=-14.0):
    """Single-pass loudnorm overshoots on 4-5 s clips: measure the .mp4, trim its audio by the difference."""
    import subprocess
    lv = _lufs(path)
    tmp = path[:-4] + "_trim.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:v", "copy", "-af",
                    f"volume={target - lv:.2f}dB", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", tmp], check=True)
    os.replace(tmp, path)
    print(f"loudness {path}: {lv:.1f} -> {_lufs(path):.1f} LUFS")


def check():
    for who in ("snip", "crinkle"):
        p = clip(who)
        ts = [i / K.DPS for i in range(int(DUR * K.DPS))]
        sq = [p.state(t, K.drawing_of(t))["sq"] for t in ts]
        t_ext = ts[max(range(len(ts)), key=lambda i: sq[i] if ts[i] < 3.0 else 0)]
        t_low = ts[min(range(len(ts)), key=lambda i: sq[i])]
        gap = round((SOUND_HIT - t_ext) * K.DPS, 2)
        print(f"{who} take: dart {T_DART:.2f} squash-low {t_low:.3f} (sq {min(sq):.3f}) extreme {t_ext:.3f} "
              f"(sq {max(sq):.3f}) hold to {T_SETTLE:.2f} grin {T_GRIN:.2f}-{DUR:.2f} "
              f"sound {SOUND_HIT:.3f} = {gap} drawing(s) after the accent {'ok' if gap == 1 else 'FAIL'}")
        closed = [t for t in ts if p.state(t, K.drawing_of(t)).get("lids") and p.state(t)["lids"][0] >= 0.9]
        print(f"{who} closed-lid drawings: {[round(t, 3) for t in closed]}")
        for t in (2.5, 3.5):                               # key object: the friend, measured from its mask
            img = Image.new("RGBA", (int(W * RES), int(H * RES)), (0, 0, 0, 0))
            p.draw(img, t, K.Cam("land", W, H, 0, 0, res=RES), K.drawing_of(t))
            fr = _frame(img, who)
            bb = fr.getchannel("A").getbbox()
            print(f"keysize {t:.2f} {100 * (bb[2] - bb[0]) / W:.1f} {who}")
        for t in ((1.5, 1.9) if who == "snip" else (1.6, 2.6)):   # the cause: bubble / leaf, from its own mask
            img = Image.new("RGBA", (int(W * RES), int(H * RES)), (0, 0, 0, 0))
            pos, ang = prop_pos(who, t, p.state(t, K.drawing_of(t)), p)
            place(img, _bubble() if who == "snip" else _leaf(), K.Cam("land", W, H, 0, 0, res=RES).S(pos),
                  angle=ang, shadow=False)
            bb = _frame(img, who).getchannel("A").getbbox()
            pct = 100 * (bb[2] - bb[0]) / W
            print(f"keysize {t:.2f} {pct:.1f} {'bubble' if who == 'snip' else 'leaf'} {'ok' if pct >= 10 else 'FAIL'}")
        hold = DUR - T_GRIN
        print(f"{who} final reaction hold {T_GRIN:.2f}-{DUR:.2f} = {hold:.2f} s {'ok' if hold >= 0.8 else 'FAIL'}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--stills"]:
        eyes_only()
    elif a == ["--strip"]:
        os.makedirs(OUT, exist_ok=True)
        for w in ("snip", "crinkle"):
            strip(w)
    elif a[:1] == ["--still"]:
        who = a[2] if len(a) > 2 else "snip"
        img, _ = render_clip(who, float(a[1]))
        path = os.path.join(OUT, f"clip_{who}_{float(a[1]):.2f}.png")
        img.convert("RGB").save(path)
        print("wrote", path)
    elif a == ["--audio"]:
        write_audio()
    elif a == ["--check"]:
        check()
    elif a == ["--render"]:
        who = os.environ.get("RIG_CLIP", "snip")
        wav = os.path.join(OUT, f"rigtest_{who}.wav")
        if not os.path.exists(wav):
            write_audio()
        out = os.path.join(ROOT, "output", f"rigtest_{who}.mp4")
        K.render_video(os.path.abspath(__file__), out, wav, DUR, "land")
        trim_loudness(out)
    else:
        sys.exit(__doc__)
