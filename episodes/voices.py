"""Wordless character voices played on instruments (the way the Clangers "talk" on slide whistles).

Snip talks on a bright slide whistle, Crinkle on a warm low hum-horn, Pip in tiny piccolo peeps.
There are no words, only the shape of speech: a question goes up, "uh-oh" falls, a giggle bubbles.
Every line returns the sound and a mouth curve, so the animation can open the mouth exactly when
the voice sounds (lip-sync).

    import voices as V
    line = V.snip("ooh")                  # or V.SNIP.say([V.S(0.3, 0, 7), ...]) for a custom line
    sfx.add(t, line.y, 0.8)
    perf.say(t, line)                     # acting.Perf opens the mouth with line.env

All sounds are synthesised here (sine partials + breath noise); no samples.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio as A  # noqa: E402

SR = A.SR
ENV_RATE = 100                         # mouth-curve samples per second
_rng = np.random.default_rng(23)


def S(dur, p0, p1=None, v=1.0, gap=0.04):
    """One syllable: `dur` seconds gliding from p0 to p1 semitones (relative to the voice's home note)."""
    return (dur, p0, p0 if p1 is None else p1, v, gap)


class Line:
    def __init__(self, y, env):
        self.y, self.env = y, env
        self.dur = len(y) / SR

    def level(self, dt):
        """Mouth opening 0..1, dt seconds after the line starts."""
        i = int(dt * ENV_RATE)
        return float(self.env[i]) if 0 <= i < len(self.env) else 0.0


class Voice:
    def __init__(self, home, partials, vib_rate=5.5, vib_depth=0.006, breath=0.08, scoop=0.6, gain=1.0):
        self.home = home                # MIDI note the voice centres on
        self.partials = partials        # [(harmonic, amplitude), ...]
        self.vib_rate, self.vib_depth = vib_rate, vib_depth
        self.breath = breath            # breathy noise around the pitch (whistle air)
        self.scoop = scoop              # each syllable starts this many semitones low and slides up
        self.gain = gain

    def say(self, sylls, vel=1.0, shift=0.0):
        total = sum(d + g for d, _, _, _, g in sylls)
        n = int((total + 0.12) * SR)
        pitch = np.zeros(n)
        amp = np.zeros(n)
        t, last = 0.0, sylls[0][1]
        for d, p0, p1, v, g in sylls:
            i0, i1 = int(t * SR), int((t + d) * SR)
            m = i1 - i0
            k = np.linspace(0, 1, m)
            k = k * k * (3 - 2 * k)
            tt = np.arange(m) / SR
            sc = self.scoop * np.exp(-tt / 0.025)
            pitch[i0:i1] = p0 + (p1 - p0) * k - sc
            att, rel = min(0.03, d / 4), min(0.06, d / 3)
            amp[i0:i1] = v * np.clip(np.minimum(tt / att, (d - tt) / rel), 0, 1)
            gap_end = min(n, int((t + d + g) * SR))
            pitch[i1:gap_end] = p1
            last = p1
            t += d + g
        pitch[int(t * SR):] = last
        tt = np.arange(n) / SR
        vib = 1 + self.vib_depth * np.sin(2 * np.pi * self.vib_rate * tt) * np.minimum(1, tt / 0.2)
        f = A.midi(self.home + shift) * 2 ** (pitch / 12) * vib
        ph = 2 * np.pi * np.cumsum(f) / SR
        y = sum(a * np.sin(h * ph) for h, a in self.partials)
        # air: slow random wobble (under ~150 Hz) ring-modulated onto the note, so the breath is a
        # narrow airy band around the pitch instead of broadband hiss
        noise = A._lowpass(A._lowpass(_rng.normal(0, 1, n), 300), 300)
        noise /= max(1e-9, noise.std())
        y = y + self.breath * noise * np.sin(ph)
        y *= amp * vel * self.gain
        env = np.clip(amp[::SR // ENV_RATE] * 1.15, 0, 1)
        return Line(y * 0.5, env)


# Snip: slide whistle around C5, bendy and bright.
SNIP = Voice(72, [(1, 1.0), (2, 0.07), (3, 0.025)], vib_rate=6.0, vib_depth=0.008, breath=0.11, scoop=0.8)
# Crinkle: warm low hum-horn around C4, an octave under Snip (overtones keep it audible on phone speakers).
CRINKLE = Voice(60, [(1, 1.0), (2, 0.6), (3, 0.34), (4, 0.16), (5, 0.07)], vib_rate=4.8, vib_depth=0.005,
                breath=0.025, scoop=0.4, gain=0.8)
# Pip: tiny piccolo peeps.
PIP = Voice(84, [(1, 1.0), (2, 0.12)], vib_rate=0, vib_depth=0, breath=0.05, scoop=1.0, gain=0.7)

SNIP_LINES = {
    "hum": [S(0.22, 0, 4), S(0.22, 4, 7), S(0.3, 7, 5), S(0.4, 5, 0, gap=0.12)],     # happy painting hum
    "hum2": [S(0.2, 4, 5), S(0.2, 7), S(0.25, 9, 7), S(0.45, 7, 4, gap=0.12)],
    "ooh": [S(0.5, 0, 8)],                                                            # curious / impressed
    "ta_da": [S(0.16, 0, 0.5), S(0.42, 7, 12)],                                       # proud: look!
    "gasp": [S(0.16, -2, 11, gap=0.02)],                                              # shock
    "aww": [S(1.0, 5, -9)],                                                           # sad, falling
    "sniff": [S(0.08, -6, -5, 0.35, 0.06), S(0.08, -5, -4, 0.3, 0.02)],
    "giggle": [S(0.07, 9, 8), S(0.07, 7, 6), S(0.07, 9, 8), S(0.09, 7, 4)],
    "hm_q": [S(0.3, 0, 0), S(0.25, 1, 8)],                                            # hmm? (question)
    "mm_ok": [S(0.2, 2, 3, 0.8), S(0.3, 0, 2, 0.8)],                                  # small, still sad "ok"
    "yay": [S(0.14, 0, 2), S(0.45, 7, 14)],
}
CRINKLE_LINES = {
    "dance": [S(0.16, 0, 0), S(0.16, 4), S(0.16, 7), S(0.16, 4), S(0.16, 0), S(0.16, 4), S(0.3, 7, 12, gap=0.1)],
    "uh_oh": [S(0.24, 4, 4), S(0.5, 1, -1)],                                          # uh-oh (falling)
    "oops": [S(0.12, 0, 5, gap=0.02)],
    "hm_q": [S(0.35, 0, 0), S(0.3, 1, 7)],                                            # what should I do?
    "sorry": [S(0.45, 3, 2), S(0.45, 0, -1), S(0.9, -3, -5, 0.8)],                   # slow, soft, falling
    "mm_hm": [S(0.18, 0), S(0.3, 5, 4)],                                              # yes / ok
    "chuckle": [S(0.08, 7, 6), S(0.08, 5, 4), S(0.08, 7, 6), S(0.12, 4, 2)],
    "fix_it": [S(0.2, 0, 2), S(0.2, 4), S(0.35, 7, 9)],                               # let's fix it! (rising)
}
PIP_LINES = {
    "peep": [S(0.08, 0, 2)],
    "peep_q": [S(0.08, 0, 1), S(0.1, 3, 8)],
    "cheep": [S(0.06, 2), S(0.06, 5), S(0.08, 7, 9)],
}


def snip(name, vel=1.0, shift=0.0):
    return SNIP.say(SNIP_LINES[name], vel, shift)


def crinkle(name, vel=1.0, shift=0.0):
    return CRINKLE.say(CRINKLE_LINES[name], vel, shift)


def pip(name, vel=1.0, shift=0.0):
    return PIP.say(PIP_LINES[name], vel, shift)
