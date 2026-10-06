"""The grown-up's arm and hands at 2x (plan N5): a port of props_grownup.GrownUpArm and props_car.hand_thumb to
hires sprites and world design units (props_grownup and props_car stay untouched for Episodes 1-10).

    import hires; hires.set_res(2)
    import props_hand2 as H
    arm = H.Arm(upper=720, fore=760)                       # sleeve segments, built once
    E = arm.draw(f, cam, shoulder, wrist, bend=+1)         # two-bone IK; bend picks the elbow side; returns elbow
    fa = arm.draw_to(f, cam, shoulder, grip, H.PINCH, bend, hand_turn=0)   # hand placed so its grip point
                                                           # lands on `grip`, forearm lined up behind it
    H.HANDS["rest" | "pinch" | "press" | "thumb" | "palm"]  # Hand(sprite, grip offset from the wrist, upright?)
    H.sleeve_end()                                         # a short second sleeve with its cuff (no hand)

Hands point along +x from the wrist ("rest", "pinch", "press": they follow the forearm); "thumb" (thumbs-up)
and "palm" (an open "wait there" palm) stay upright at the wrist. "pinch" holds a small thing (a stem, a tea
light) between thumb and fingers at its grip point; "press" is the same with the thumb pressed in (a click).
Sizes: the hand is about 140 units long (a grown-up's hand next to a 240-unit pumpkin). No tools, ever.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scene  # noqa: E402
from hires import Cut  # noqa: E402
from paperlib import mix, place, rot  # noqa: E402

SLEEVE = scene.SLEEVE
SLEEVE_DARK = mix(SLEEVE, (40, 50, 90), 0.35)
SLEEVE_LIGHT = mix(SLEEVE, (255, 255, 255), 0.22)
CUFF = (244, 244, 248)
SKIN = scene.SKIN
SKIN_LINE = (182, 126, 92)
NAIL = (232, 186, 156)


def _ang(dx, dy):
    """place() angle (deg CCW) that turns +x toward the vector (dx, dy) (y down)."""
    return math.degrees(math.atan2(-dy, dx))


def _segment(length, w0, w1, crease_at_end=False, cuff=False):
    pad = max(w0, w1) / 2 + 6
    W, H = length + 2 * pad, max(w0, w1) + 12
    cy = H / 2
    c = Cut(W, H)
    x0, x1 = pad, pad + length
    c.polygon([(x0, cy - w0 / 2), (x1, cy - w1 / 2), (x1, cy + w1 / 2), (x0, cy + w0 / 2)], SLEEVE)
    c.ellipse(x0, cy, w0 / 2, w0 / 2, SLEEVE)
    c.ellipse(x1, cy, w1 / 2, w1 / 2, SLEEVE)
    c.polygon([(x0 + 8, cy - w0 / 2 + 7), (x1 - 8, cy - w1 / 2 + 7), (x1 - 8, cy - w1 / 2 + 15),
               (x0 + 8, cy - w0 / 2 + 16)], SLEEVE_LIGHT, sil=False)
    c.line([(x0 + 0.25 * length, cy + w0 * 0.22), (x0 + 0.7 * length, cy + w1 * 0.24)], 3, SLEEVE_DARK)
    if crease_at_end:
        for k, dx in ((0, -40), (1, -24)):
            r = w1 * 0.36
            c.arc(x1 + dx, cy, r * 0.55, r, 120 + 10 * k, 240 - 10 * k, 3, SLEEVE_DARK)
    if cuff:
        c.rrect(x1 - 20, cy - w1 / 2 - 4, x1 + 9, cy + w1 / 2 + 4, 8, CUFF)
    return c.finish(pivot=(x0, cy), border=4, shadow_alpha=0.26)


class Hand:
    def __init__(self, spr, grip=(0.0, 0.0), upright=False):
        self.spr, self.grip, self.upright = spr, grip, upright


def _fingers(c, x0, ys, lens, w=17):
    for y, L in zip(ys, lens):
        c.rrect(x0, y - w / 2, x0 + L, y + w / 2, w / 2, SKIN)
        c.ellipse(x0 + L - 7, y, 4.5, 3.6, NAIL, sil=False)


def hand_rest():
    """Flat steadying hand, fingers along +x and curving down a little at the tips; pivot = wrist."""
    c = Cut(170, 110)
    c.rrect(8, 26, 84, 88, 26, SKIN)
    _fingers(c, 60, (34, 50, 66, 81), (138, 148, 144, 128), w=16)
    c.ellipse(52, 18, 32, 12, SKIN, theta=-16)                     # thumb along the top
    for y in (42, 58, 74):
        c.line([(86, y), (118, y)], 2, SKIN_LINE)
    return Hand(c.finish(pivot=(8, 57), border=4, shadow_alpha=0.26))


def hand_pinch(pressed=False):
    """Loose fist from above-side, thumb and index meeting at the grip point (GRIP) ahead of the knuckles."""
    c = Cut(170, 120)
    c.rrect(8, 30, 96, 96, 30, SKIN)                               # palm / back of the hand
    for i, y in enumerate((44, 60, 76, 90)):                       # curled fingers (knuckle row)
        c.ellipse(98 - 3 * i, y, 16, 9, SKIN)
    c.rrect(92, 50, 128, 66, 8, SKIN)                              # index reaching forward
    c.ellipse(123, 58, 4.5, 3.6, NAIL, sil=False)
    tx = 112 if not pressed else 117                               # thumb (pressed: pushed in a little)
    c.rrect(58, 22, tx + 12, 38, 8, SKIN)
    c.ellipse(tx + 6, 30, 4.5, 3.6, NAIL, sil=False)
    for y in (52, 68):
        c.line([(70, y), (92, y)], 2, SKIN_LINE)
    return Hand(c.finish(pivot=(8, 63), border=4, shadow_alpha=0.26), grip=(120, -19))


def hand_thumb():
    """Thumbs-up: a fist (knuckles right) with the thumb straight up; pivot = wrist (left), upright."""
    c = Cut(130, 150)
    c.rrect(14, 62, 104, 128, 26, SKIN)
    for y in (74, 89, 104, 118):
        c.ellipse(104, y, 12, 9, SKIN)
    for y in (82, 97, 111):
        c.line([(70, y), (102, y)], 2, SKIN_LINE)
    c.rrect(46, 10, 76, 76, 15, SKIN)
    c.ellipse(61, 22, 8, 6, NAIL, sil=False)
    return Hand(c.finish(pivot=(14, 98), border=4, shadow_alpha=0.26), upright=True)


def hand_palm():
    """Open palm facing us, fingers up: "wait there". Pivot = wrist (bottom), upright."""
    c = Cut(130, 170)
    c.rrect(22, 70, 106, 150, 30, SKIN)
    for x, L in ((32, 72), (52, 84), (72, 82), (92, 70)):
        c.rrect(x - 8, 92 - L, x + 8, 100, 8, SKIN)
        c.ellipse(x, 92 - L + 8, 3.6, 4.5, NAIL, sil=False)
    c.ellipse(112, 112, 12, 26, SKIN, theta=-30)                   # thumb
    c.arc(64, 118, 22, 10, 20, 160, 2, SKIN_LINE)
    return Hand(c.finish(pivot=(64, 150), border=4, shadow_alpha=0.26), upright=True)


HANDS = {}


def _build_hands():
    if not HANDS:
        HANDS.update(rest=hand_rest(), pinch=hand_pinch(False), press=hand_pinch(True), thumb=hand_thumb(),
                     palm=hand_palm())
    return HANDS


def sleeve_end():
    """A short piece of the second sleeve with its cuff (pivot at the cuff end; the sleeve lies along -x)."""
    spr = _segment(110, 78, 70, cuff=True)
    return spr


class Arm:
    def __init__(self, upper=720, fore=760, w_shoulder=104, w_elbow=90, w_wrist=74):
        self.L1, self.L2 = upper, fore
        self.upper = _segment(upper, w_shoulder, w_elbow, crease_at_end=True)
        self.fore = _segment(fore, w_elbow, w_wrist, cuff=True)
        _build_hands()

    def solve(self, S, W, bend):
        dx, dy = W[0] - S[0], W[1] - S[1]
        d = math.hypot(dx, dy)
        d = max(abs(self.L1 - self.L2) + 1.0, min(d, self.L1 + self.L2 - 1.0))
        a = math.atan2(dy, dx)
        phi = math.acos(max(-1.0, min(1.0, (self.L1 ** 2 + d ** 2 - self.L2 ** 2) / (2 * self.L1 * d))))
        e = a + bend * phi
        E = (S[0] + self.L1 * math.cos(e), S[1] + self.L1 * math.sin(e))
        b = math.atan2(W[1] - E[1], W[0] - E[0])
        reach = (E[0] + self.L2 * math.cos(b), E[1] + self.L2 * math.sin(b))
        off = (W[0] - reach[0], W[1] - reach[1])                   # out of reach: the shoulder slides along
        return (E[0] + off[0], E[1] + off[1]), (S[0] + off[0], S[1] + off[1])

    def draw(self, f, cam, shoulder, wrist, bend=1):
        E, S = self.solve(shoulder, wrist, bend)
        place(f, self.upper, cam.S(S), angle=_ang(E[0] - S[0], E[1] - S[1]))
        fa = _ang(wrist[0] - E[0], wrist[1] - E[1])
        place(f, self.fore, cam.S(E), angle=fa)
        return E, fa

    def wrist_for(self, shoulder, grip, hand, bend=1, hand_turn=0.0):
        """Wrist position that puts the hand's grip point on `grip` (the hand follows the forearm + hand_turn)."""
        W = grip
        for _ in range(6):
            E, _S = self.solve(shoulder, W, bend)
            fa = _ang(W[0] - E[0], W[1] - E[1]) + hand_turn
            gx, gy = rot(hand.grip[0], hand.grip[1] - 0.0, fa)
            W = (grip[0] - gx, grip[1] - gy)
        return W

    def draw_hand(self, f, cam, shoulder, wrist, hand, bend=1, hand_turn=0.0, alpha=1.0):
        """Arm to `wrist`, then the hand (following the forearm, or upright). Returns the grip point (world)."""
        E, fa = self.draw(f, cam, shoulder, wrist, bend)
        ang = 0.0 if hand.upright else fa + hand_turn
        place(f, hand.spr, cam.S(wrist), angle=ang, alpha=alpha)
        gx, gy = rot(hand.grip[0], hand.grip[1], ang)
        return wrist[0] + gx, wrist[1] + gy
