"""Episode 1 — Hot Cup! Wait before you touch.

Run:  python3 episodes/ep01_hot_cup.py            (full render -> output/)
      python3 episodes/ep01_hot_cup.py --stills    (contact sheet of key moments)
"""
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import audio as A  # noqa: E402
import scene  # noqa: E402
from characters import Character  # noqa: E402
from paperlib import ease_in_out, ease_out, ease_out_back, lerp, place, seg  # noqa: E402

FPS = 30
DUR = 25.0
TY = scene.TABLE_Y
CUP_X = 540
SNIP_X = 250
CR_X = 815
CR_REST_L = 346   # Crinkle's left arm hanging (same as -14, but swings outward when raised)

BG = scene.background()
CUP = scene.cup()
STEAM = scene.steam_frames(16)
SIGN_NO = scene.sign_no_touch()
SIGN_OK = scene.sign_ok()
PUFF = scene.puff()
Q = scene.icon("❓")
EX = scene.icon("❗")
HEARTS = [scene.heart(c) for c in ((240, 72, 98), (255, 120, 150), (244, 92, 120))]
BANNER = scene.banner("HOT? WAIT!", "🔥", "✋")
SNIP = Character("snip", 1.0)
CR = Character("crinkle", 1.1)

HEART_PLAN = [(19.6 + i * 0.32, x, y) for i, (x, y) in
              enumerate(((170, 560), (910, 640), (390, 470), (700, 520), (560, 690), (260, 800), (860, 840)))]
PUFFS = (15.4, 16.3, 17.2)


def hops(t, t0, t1, n, height):
    p = seg(t, t0, t1)
    return height * abs(math.sin(math.pi * n * p)) if 0 < p < 1 else 0.0


def pop_scale(t, t0, d=0.35):
    return ease_out_back(seg(t, t0, t0 + d))


def snip_state(t):
    s = dict(x=SNIP_X, hop=0.0, lean=0.0, arm_l=-14, arm_r=14, eyes="normal", mouth="w", look=(0, 0), head_dy=0)
    if t < 2.4:  # hop in
        p = seg(t, 0.6, 2.4)
        s["x"] = lerp(-240, SNIP_X, ease_in_out(p))
        s["hop"] = hops(t, 0.6, 2.4, 3, 75)
        s["lean"] = -6 if 0 < p < 1 else 0
        sw = 18 * math.sin(t * 14)
        s["arm_l"], s["arm_r"] = -14 - sw, 14 + sw
        s["eyes"] = "happy"
    elif t < 3.2:  # notices the cup
        s.update(eyes="wide", mouth="o", look=(6, 2))
    elif t < 7.6:  # slowly reaches for it
        p = ease_in_out(seg(t, 3.2, 6.9))
        s.update(arm_r=lerp(14, 72, p), lean=lerp(0, -7, p), look=(6, 2), mouth="w")
    elif t < 10.4:  # sign! freeze
        s.update(arm_r=72, lean=-7, eyes="wide" if t < 8.4 else "worried",
                 mouth="o" if t < 8.4 else "wobble", look=(6, -4))
        s["hop"] = hops(t, 7.6, 7.95, 1, 28)
    elif t < 12.0:  # pulls paw back
        p = ease_out(seg(t, 10.4, 10.8))
        s.update(arm_r=lerp(72, 14, p), lean=lerp(-7, 0, p), eyes="worried", mouth="wobble", look=(5, -1))
    elif t < 15.0:  # understands — nods
        s.update(eyes="normal", mouth="w", look=(4, 0))
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 12.3, 12.65)) + math.sin(math.pi * seg(t, 12.9, 13.25)))
    elif t < 18.4:  # watches Crinkle blow
        s.update(look=(7, 0), mouth="o" if 16.0 < t < 17.8 else "w")
    elif t < 19.0:
        s.update(eyes="wide", mouth="grin")
    else:  # celebrate
        s.update(eyes="happy", mouth="grin")
        s["hop"] = hops(t, 19.2, 23.6, 4, 60)
        wave = 14 * math.sin(t * 9)
        raise_p = ease_out(seg(t, 19.0, 19.3))
        s["arm_l"] = lerp(-14, -150 + wave, raise_p)
        s["arm_r"] = lerp(14, 150 - wave, raise_p)
    return s


def crinkle_state(t):
    s = dict(x=CR_X, hop=0.0, lean=0.0, arm_l=CR_REST_L, arm_r=14, eyes="normal", mouth="smile",
             look=(0, 0), head_dy=0, sign=None, sign_scale=0.0)
    if t < 7.0:
        s["x"] = 1400
        return s
    if t < 10.4:  # slides in with the sign
        p = seg(t, 7.0, 7.55)
        s["x"] = lerp(1400, CR_X, ease_out_back(p, 1.2))
        s["lean"] = 10 * (1 - ease_out(seg(t, 7.0, 7.9)))
        s["arm_l"] = lerp(CR_REST_L, 192, ease_out_back(seg(t, 7.4, 7.7)))
        s.update(eyes="worried", mouth="o", look=(-5, 0), sign=SIGN_NO, sign_scale=pop_scale(t, 7.5))
        if t > 10.0:
            s["sign_scale"] = 1 - ease_in_out(seg(t, 10.0, 10.35))
            s["arm_l"] = lerp(192, 226, ease_in_out(seg(t, 10.0, 10.4)))
    elif t < 12.0:  # points at the steam
        wag = 4 * math.sin(t * 12) if t < 11.6 else 0
        back = ease_in_out(seg(t, 11.6, 12.0))
        s.update(arm_l=lerp(226 + wag, CR_REST_L, back), eyes="normal", mouth="o", look=(-6, 1))
    elif t < 15.0:  # nods with Snip
        s.update(eyes="happy", mouth="smile")
        s["head_dy"] = 14 * (math.sin(math.pi * seg(t, 12.6, 12.95)) + math.sin(math.pi * seg(t, 13.2, 13.55)))
    elif t < 18.3:  # blows on the cup
        pulse = sum(3 * math.sin(math.pi * seg(t, p0, p0 + 0.5)) for p0 in PUFFS)
        s.update(lean=9 * ease_out(seg(t, 15.0, 15.3)) + pulse, mouth="blow", eyes="normal", look=(-6, 2))
    else:  # it's cool now — OK sign, celebrate
        s["lean"] = 9 * (1 - ease_out(seg(t, 18.3, 18.6)))
        s.update(eyes="happy", mouth="grin", sign=SIGN_OK, sign_scale=pop_scale(t, 18.45))
        s["arm_l"] = lerp(CR_REST_L, 192, ease_out_back(seg(t, 18.35, 18.65)))
        s["hop"] = hops(t, 19.5, 23.9, 4, 50)
        s["arm_r"] = lerp(14, 150 + 18 * math.sin(t * 8), ease_out(seg(t, 19.0, 19.3)))
    return s


def render_frame(t):
    f = BG.copy()
    place(f, CUP, (CUP_X, TY + 8))

    # steam: wiggles, then gets blown away (to the left) and fades
    blown = ease_in_out(seg(t, 15.4, 18.0))
    for i, dx in enumerate((-45, 0, 45)):
        idx = (int(t * 12) + i * 5) % len(STEAM)
        a = (1 - blown) * (0.95 - 0.1 * i)
        place(f, STEAM[idx], (CUP_X + dx - 60 * blown, 1268 - 40 * blown), alpha=a,
              angle=14 * blown)

    sn = snip_state(t)
    SNIP.draw(f, sn["x"], TY, hop=sn["hop"], lean=sn["lean"], arm_l=sn["arm_l"], arm_r=sn["arm_r"],
              eyes=sn["eyes"], mouth=sn["mouth"], look=sn["look"], head_dy=sn["head_dy"])

    cr = crinkle_state(t)
    if cr["sign"] is not None and cr["sign_scale"] > 0.01:
        tip = CR.paw_tip(cr["x"], TY, "l", cr["arm_l"], cr["hop"], cr["lean"])
        place(f, cr["sign"], tip, scale=cr["sign_scale"], angle=3 * math.sin(t * 5))
    CR.draw(f, cr["x"], TY, hop=cr["hop"], lean=cr["lean"], arm_l=cr["arm_l"], arm_r=cr["arm_r"],
            eyes=cr["eyes"], mouth=cr["mouth"], look=cr["look"], head_dy=cr["head_dy"])

    for p0 in PUFFS:  # breath puffs travelling from Crinkle to the steam
        p = seg(t, p0, p0 + 0.75)
        if 0 < p < 1:
            x, y = lerp(655, 545, ease_out(p)), lerp(1120, 1165, p)
            place(f, PUFF, (x, y), scale=lerp(0.6, 1.05, p), alpha=math.sin(math.pi * p))

    if 2.5 < t < 3.3:
        place(f, Q, (SNIP_X + 70, 730 - 10 * math.sin(t * 8)), scale=pop_scale(t, 2.5, 0.25))
    if 7.65 < t < 8.8:
        place(f, EX, (SNIP_X + 70, 730), scale=pop_scale(t, 7.65, 0.25))

    for i, (t0, x, y) in enumerate(HEART_PLAN):
        if t > t0:
            p = ease_out(seg(t, t0, t0 + 0.9))
            place(f, HEARTS[i % 3], (x + 10 * math.sin(t * 3 + i), lerp(-90, y, p) + 6 * math.sin(t * 4 + i)),
                  angle=10 * math.sin(t * 2.5 + i), scale=0.8 + 0.2 * p)

    if t > 22.3:
        place(f, BANNER, (540, 300), scale=pop_scale(t, 22.3, 0.45), angle=2 * math.sin(t * 3))
    return camera(f, t)


CAM_KEYS = [  # (time, zoom, center x, center y) — gentle push-ins on the tense moments
    (0.0, 1.0, 540, 960), (2.4, 1.0, 540, 960), (3.2, 1.08, 420, 1150), (6.9, 1.16, 430, 1180),
    (7.0, 1.16, 430, 1180), (7.5, 1.0, 540, 960), (15.0, 1.0, 540, 960), (15.6, 1.1, 660, 1150),
    (18.2, 1.1, 660, 1150), (18.7, 1.0, 540, 960), (DUR, 1.0, 540, 960)]


def camera(f, t):
    for (t0, z0, x0, y0), (t1, z1, x1, y1) in zip(CAM_KEYS, CAM_KEYS[1:]):
        if t0 <= t <= t1:
            k = ease_in_out(seg(t, t0, t1))
            z, cx, cy = lerp(z0, z1, k), lerp(x0, x1, k), lerp(y0, y1, k)
            break
    else:
        return f
    if z < 1.001:
        return f
    w, h = scene.W / z, scene.H / z
    left = min(max(cx - w / 2, 0), scene.W - w)
    top = min(max(cy - h / 2, 0), scene.H - h)
    from PIL import Image
    return f.resize((scene.W, scene.H), Image.BICUBIC, box=(left, top, left + w, top + h))


def build_audio(path):
    b = 60 / 112
    music, sfx = A.Mix(DUR), A.Mix(DUR)
    # A: bouncy intro
    for beat, m in ((0, 72), (0.5, 76), (1, 79), (1.5, 76), (2, 81), (2.5, 79), (3, 76), (3.5, 79),
                    (4, 77), (4.5, 76), (5, 74)):
        music.add(0.15 + beat * b, A.marimba(A.midi(m), 0.6, 0.7))
    for beat, m in ((0, 48), (1, 55), (2, 57), (3, 55), (4, 53), (5, 55)):
        music.add(0.15 + beat * b, A.bass(A.midi(m), 0.45, 0.8))
    for k in range(11):
        music.add(0.15 + (k + 0.5) * b, A.shaker(0.6))
    # B: tiptoe tension while Snip reaches
    for i, m in enumerate(range(52, 60)):
        music.add(3.25 + i * 0.47, A.pluck(A.midi(m), 0.4, 0.45 + i * 0.06))
    # C: the sign — soft "hmm" pad
    music.add(7.8, A.pad([A.midi(48), A.midi(55), A.midi(62)], 2.8, 0.35))
    # D: understanding — gentle marimba
    for tt, m in ((11.2, 76), (11.75, 74), (12.3, 72), (13.4, 67), (13.95, 72)):
        music.add(tt, A.marimba(A.midi(m), 0.8, 0.5))
    music.add(15.2, A.pad([A.midi(48), A.midi(52), A.midi(55)], 3.0, 0.25))
    # F: happy jingle + final chord
    t0 = 19.0
    mel = ((0, 72), (0.5, 74), (1, 76), (1.5, 79), (2, 81), (3, 79), (3.5, 76), (4, 77), (4.5, 79),
           (5, 76), (6, 74), (6.5, 76), (7, 72), (8, 72), (8.5, 76))
    for beat, m in mel:
        music.add(t0 + beat * b, A.marimba(A.midi(m), 0.7, 0.8))
    for beat, m in ((0, 48), (1, 43), (2, 45), (3, 40), (4, 41), (5, 43), (6, 48), (7, 43), (8, 48)):
        music.add(t0 + beat * b, A.bass(A.midi(m), 0.45, 0.9))
    for k in range(18):
        music.add(t0 + (k * 0.5 + 0.25) * b, A.shaker(0.5))
    for beat in (1, 3, 5, 7):
        music.add(t0 + beat * b, A.clap(0.7))
    end = t0 + 9 * b
    for m in (60, 64, 67, 72):
        music.add(end, A.marimba(A.midi(m), 1.6, 0.6))
    music.add(end, A.chime_up(0.6, (72, 76, 79, 84)))
    music.add(end, A.bass(A.midi(36), 1.2, 1.0))

    # sound effects
    sfx.add(0.6, A.boing(0.8))
    for tt in (1.2, 1.8, 2.4):
        sfx.add(tt - 0.02, A.tap(0.9))
    sfx.add(2.5, A.pop(0.6))
    sfx.add(6.95, A.whoosh(0.55, 1.0))
    sfx.add(7.5, A.glock(A.midi(91), 1.2, 0.9))
    sfx.add(7.56, A.glock(A.midi(88), 1.2, 0.6))
    sfx.add(7.65, A.pop(0.7))
    sfx.add(10.0, A.whoosh(0.35, 0.5))
    sfx.add(10.4, A.zip_down(0.8))
    for tt in (12.3, 12.6, 12.9, 13.2):
        sfx.add(tt, A.tap(0.45))
    for tt in PUFFS:
        sfx.add(tt - 0.05, A.blow(0.75, 1.0))
    sfx.add(18.1, A.chime_up(1.0))
    sfx.add(18.45, A.pop(0.7))
    for tt, _, _ in HEART_PLAN:
        sfx.add(tt, A.pop(0.45))
    for k in range(4):
        sfx.add(19.2 + k * 1.1, A.boing(0.35, 300))
    sfx.add(22.3, A.glock(A.midi(96), 1.0, 0.6))

    y = 0.55 * music.normalized() + 0.75 * sfx.normalized()
    A.write_wav(path, y / max(1.0, abs(y).max() / 0.95))


def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(ROOT, "build", "ep01_audio.wav")
    build_audio(wav)
    out = os.path.join(out_dir, "ep01_hot_cup.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{scene.W}x{scene.H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS)
    t0 = time.time()
    for i in range(n):
        proc.stdin.write(render_frame(i / FPS).convert("RGB").tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out, f"in {time.time() - t0:.0f}s")
    return out


def stills(path):
    from PIL import Image
    times = [1.5, 2.8, 5.5, 8.0, 10.9, 12.5, 16.4, 18.8, 21.0, 23.5]
    thumbs = [render_frame(t).convert("RGB").resize((270, 480)) for t in times]
    sheet = Image.new("RGB", (270 * 5, 480 * 2), "white")
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % 5) * 270, (i // 5) * 480))
    sheet.save(path)
    print("wrote", path)


if __name__ == "__main__":
    if "--stills" in sys.argv:
        stills(os.path.join(ROOT, "build", "ep01_stills.png"))
    else:
        render(os.path.join(ROOT, "output"))
