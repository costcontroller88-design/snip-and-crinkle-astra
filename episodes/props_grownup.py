"""The grown-up's arm, version 2: a jointed paper arm (upper arm + elbow + forearm + cuff + hand).

Replaces the old "pole" arm (one long straight sleeve hanging from the top of the frame) used in
Episodes 5 and 9. The arm is solved each frame with two-bone IK from a shoulder that sits off-frame,
so it always shows a soft elbow bend, a tapered sleeve with an elbow crease, a white cuff and a hand.
Only the joint angles change per frame; the paper sprites themselves are built once.

    arm = GrownUpArm(upper=760, fore=700, bend=-1)       # bend -1: elbow to the left of shoulder->wrist
    arm.draw(frame, shoulder=(x, y), wrist=(x, y))        # draws sleeve segments, returns forearm angle
    arm.draw_reaching(frame, shoulder, tip, hand)         # same, but places `hand` so its tip lands on `tip`

Shared modules are untouched (EPISODE_GUIDE rule); colours come from scene.py.
"""
import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scene  # noqa: E402
from paperlib import Cut, Sprite, mix, place  # noqa: E402

SLEEVE = scene.SLEEVE
SLEEVE_DARK = mix(SLEEVE, (40, 50, 90), 0.35)
SLEEVE_LIGHT = mix(SLEEVE, (255, 255, 255), 0.22)
CUFF = (244, 244, 248)
SKIN = scene.SKIN
SKIN_LINE = (182, 126, 92)


def _segment(length, w0, w1, crease_at_end=False, cuff=False):
    """A tapered sleeve segment lying along +x. Pivot = the joint at x=0 (centre line).
    Rounded ends overlap neighbouring segments so the elbow reads as one bent sleeve."""
    pad = max(w0, w1) // 2 + 6
    W, H = int(length + 2 * pad), int(max(w0, w1) + 12)
    cy = H / 2
    c = Cut(W, H)
    x0, x1 = pad, pad + length
    pts = [(x0, cy - w0 / 2), (x1, cy - w1 / 2), (x1, cy + w1 / 2), (x0, cy + w0 / 2)]
    c.polygon(pts, SLEEVE)
    c.ellipse(x0, cy, w0 / 2, w0 / 2, SLEEVE)
    c.ellipse(x1, cy, w1 / 2, w1 / 2, SLEEVE)
    # paper highlight along the top edge and a soft fold line underneath
    c.polygon([(x0 + 10, cy - w0 / 2 + 10), (x1 - 10, cy - w1 / 2 + 10),
               (x1 - 10, cy - w1 / 2 + 22), (x0 + 10, cy - w0 / 2 + 24)], SLEEVE_LIGHT, sil=False)
    c.line([(x0 + 0.25 * length, cy + w0 * 0.22), (x0 + 0.7 * length, cy + w1 * 0.24)], 4, SLEEVE_DARK)
    if crease_at_end:                                   # elbow creases (two little curved folds)
        for k, dx in ((0, -58), (1, -34)):
            r = w1 * 0.36
            c.arc(x1 + dx, cy, r * 0.55, r, 120 + 10 * k, 240 - 10 * k, 4, SLEEVE_DARK)
    if cuff:                                            # white shirt cuff at the wrist end
        c.rrect(x1 - 30, cy - w1 / 2 - 6, x1 + 14, cy + w1 / 2 + 6, 12, CUFF)
    return c.finish(pivot=(x0, cy), border=5, shadow_alpha=0.26)


def hand_open(mirror=False):
    """Open hand pointing along +x (fingers to the right), thumb on the top side.
    Pivot = the wrist (left). Returns (sprite, length wrist->fingertips)."""
    c = Cut(230, 150)
    c.rrect(14, 30, 120, 122, 38, SKIN)                 # palm
    for i, y in enumerate((38, 62, 86, 108)):           # four fingers
        L = (186, 202, 196, 176)[i]
        c.rrect(80, y - 13, L, y + 13, 13, SKIN)
    for y in (50, 74, 97):
        c.line([(118, y), (170, y)], 3, SKIN_LINE)
    c.ellipse(78, 18, 46, 17, SKIN, theta=-18)          # thumb
    spr = c.finish(pivot=(12, 76), border=4, shadow_alpha=0.28)
    if mirror:
        spr = Sprite(spr.img.transpose(Image.FLIP_TOP_BOTTOM), (spr.pivot[0], spr.img.height - spr.pivot[1]),
                     spr.shadow.transpose(Image.FLIP_TOP_BOTTOM))
    return spr, 196


def _ang(dx, dy):
    """paperlib.place angle (deg CCW) that turns +x toward screen vector (dx, dy)."""
    return math.degrees(math.atan2(-dy, dx))


class GrownUpArm:
    def __init__(self, upper=760, fore=700, bend=-1, w_shoulder=150, w_elbow=128, w_wrist=104):
        self.L1, self.L2, self.bend = upper, fore, bend
        self.upper = _segment(upper, w_shoulder, w_elbow, crease_at_end=True)
        self.fore = _segment(fore, w_elbow, w_wrist, cuff=True)

    def solve(self, S, W):
        """Two-bone IK: elbow position for shoulder S and wrist W."""
        dx, dy = W[0] - S[0], W[1] - S[1]
        d = math.hypot(dx, dy)
        d = max(abs(self.L1 - self.L2) + 1.0, min(d, self.L1 + self.L2 - 1.0))
        a = math.atan2(dy, dx)
        phi = math.acos(max(-1.0, min(1.0, (self.L1 ** 2 + d ** 2 - self.L2 ** 2) / (2 * self.L1 * d))))
        e = a + self.bend * phi
        E = (S[0] + self.L1 * math.cos(e), S[1] + self.L1 * math.sin(e))
        # if the target is out of reach, slide the shoulder toward it so the wrist still lands exactly
        reach = (E[0] + self.L2 * math.cos(math.atan2(W[1] - E[1], W[0] - E[0])),
                 E[1] + self.L2 * math.sin(math.atan2(W[1] - E[1], W[0] - E[0])))
        off = (W[0] - reach[0], W[1] - reach[1])
        return (E[0] + off[0], E[1] + off[1]), (S[0] + off[0], S[1] + off[1])

    def draw(self, f, shoulder, wrist):
        E, S = self.solve(shoulder, wrist)
        place(f, self.upper, S, angle=_ang(E[0] - S[0], E[1] - S[1]))
        fa = _ang(wrist[0] - E[0], wrist[1] - E[1])
        place(f, self.fore, E, angle=fa)              # |wrist - E| == L2, so the cuff lands on the wrist
        return fa

    def draw_reaching(self, f, shoulder, tip, hand, hand_len):
        """Place the hand so its fingertips land on `tip`, with the forearm lined up behind it."""
        u = (tip[0] - shoulder[0], tip[1] - shoulder[1])
        for _ in range(3):                            # wrist = tip - hand_len * forearm direction
            n = math.hypot(*u) or 1.0
            W = (tip[0] - hand_len * u[0] / n, tip[1] - hand_len * u[1] / n)
            E, _S = self.solve(shoulder, W)
            u = (W[0] - E[0], W[1] - E[1])
        fa = self.draw(f, shoulder, W)
        place(f, hand, W, angle=fa)
        return W
