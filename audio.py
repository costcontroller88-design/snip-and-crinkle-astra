"""Tiny synth for original, copyright-free music and sound effects."""
import wave

import numpy as np

SR = 44100
_rng = np.random.default_rng(11)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _attack(t, k=900):
    return 1 - np.exp(-t * k)


def _lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


# instruments
def marimba(f, dur=0.7, vel=1.0):
    t = _t(dur)
    y = (np.sin(2 * np.pi * f * t)
         + 0.28 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 18)
         + 0.08 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 40))
    return vel * np.exp(-t * 6.5) * _attack(t) * y


def glock(f, dur=1.3, vel=1.0):
    t = _t(dur)
    y = sum(a * np.exp(-t * d) * np.sin(2 * np.pi * f * r * t)
            for r, a, d in ((1, 1, 3.0), (2.76, 0.4, 6), (5.4, 0.2, 10), (8.93, 0.1, 16)))
    return vel * _attack(t, 2000) * y


def pluck(f, dur=0.4, vel=1.0):
    t = _t(dur)
    y = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 20)
         + 0.25 * np.sin(6 * np.pi * f * t) * np.exp(-t * 30))
    return vel * np.exp(-t * 13) * _attack(t, 600) * y


def bass(f, dur=0.45, vel=1.0):
    t = _t(dur)
    return vel * np.exp(-t * 5) * _attack(t, 300) * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))


def pad(fs, dur=2.5, vel=1.0):
    t = _t(dur)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return vel * env * sum(np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t) for f in fs) / len(fs)


def shaker(vel=1.0):
    t = _t(0.09)
    n = np.diff(_rng.normal(0, 1, len(t)), prepend=0)
    return vel * 0.25 * np.exp(-t * 55) * _attack(t, 3000) * n


def clap(vel=1.0):
    t = _t(0.16)
    n = _rng.normal(0, 1, len(t))
    n = n - _lowpass(n, 12)
    env = np.exp(-t * 30) * _attack(t, 4000)
    return vel * 0.45 * env * n


# sound effects
def boing(vel=1.0, base=260):
    t = _t(0.5)
    f = base + 120 * np.exp(-5 * t) * np.sin(2 * np.pi * 11 * t) + 160 * t
    return vel * np.exp(-6 * t) * _attack(t, 800) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def pop(vel=1.0):
    t = _t(0.1)
    f = 450 + 8000 * t
    return vel * np.exp(-t * 45) * _attack(t, 3000) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def tap(vel=1.0):
    t = _t(0.18)
    f = 150 - 60 * t
    return vel * np.exp(-t * 28) * _attack(t, 2000) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def whoosh(dur=0.55, vel=1.0):
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    y = _lowpass(n, 5) - _lowpass(n, 40)
    return vel * 0.9 * np.sin(np.pi * t / dur) ** 2 * y


def blow(dur=0.75, vel=1.0):
    t = _t(dur)
    n = _rng.normal(0, 1, len(t))
    y = _lowpass(n, 18) - _lowpass(n, 120)
    env = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.25) * 5)
    return vel * 1.6 * env * y


def zip_down(vel=1.0):
    t = _t(0.25)
    f = 900 * np.exp(-t * 7) + 200
    return vel * 0.5 * np.exp(-t * 6) * _attack(t) * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4


def chime_up(vel=1.0, notes=(84, 88, 91, 96)):
    out = np.zeros(int(1.8 * SR))
    for i, m in enumerate(notes):
        g = glock(midi(m), 1.3, vel * 0.7)
        s = int(i * 0.08 * SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


class Mix:
    def __init__(self, dur):
        self.dur = dur
        self.buf = np.zeros(int((dur + 3) * SR))

    def add(self, t, sig, gain=1.0):
        i = int(t * SR)
        if i >= len(self.buf):
            return
        n = min(len(sig), len(self.buf) - i)
        self.buf[i:i + n] += gain * sig[:n]

    def normalized(self, peak=0.9):
        y = self.buf[:int(self.dur * SR)].copy()
        m = np.max(np.abs(y)) or 1
        return y * (peak / m)


def write_wav(path, y, fade_out=0.35):
    y = y.copy()
    n = int(fade_out * SR)
    y[-n:] *= np.linspace(1, 0, n)
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    stereo = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())


# ---------------------------------------------------------------- v2 sound kit
def ks_pluck(f, dur=1.2, vel=1.0, decay=0.996, bright=0.6):
    """Karplus-Strong plucked string (ukulele-ish)."""
    N = max(2, int(SR / f))
    n = int(dur * SR)
    out = np.zeros(n + N)
    noise = _rng.uniform(-1, 1, N)
    out[:N] = bright * noise + (1 - bright) * np.convolve(noise, [0.5, 0.5], mode="same")
    for start in range(N, n + N, N):
        prev = out[start - N:start]
        before = out[start - N - 1] if start - N - 1 >= 0 else 0.0
        nxt = decay * 0.5 * (prev + np.concatenate(([before], prev[:-1])))
        end = min(start + N, len(out))
        out[start:end] = nxt[:end - start]
    y = out[:n]
    t = _t(dur)
    return vel * 0.8 * y * _attack(t, 3000)


UKE_CHORDS = {"C": (67, 60, 64, 72), "F": (69, 60, 65, 69), "G": (67, 62, 71, 74),
              "Am": (69, 60, 64, 69), "G7": (67, 62, 65, 71), "Dm": (69, 62, 65, 69)}


def strum(mix, t, chord, vel=1.0, up=False, gain=1.0):
    notes = UKE_CHORDS[chord]
    order = reversed(notes) if up else notes
    for i, m in enumerate(order):
        mix.add(t + i * 0.014, ks_pluck(midi(m), 1.1, vel * (0.9 if up else 1.0)), gain)


def woodblock(high=True, vel=1.0):
    t = _t(0.07)
    f = 1350 if high else 950
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t)
    return vel * 0.6 * np.exp(-t * 70) * _attack(t, 5000) * y


def psshh(vel=1.0):
    t = _t(0.9)
    n = _rng.normal(0, 1, len(t))
    y = n - _lowpass(n, 3)
    env = _attack(t, 400) * np.exp(-t * 3.2)
    return vel * 0.9 * env * y


def slurp(vel=1.0):
    t = _t(0.7)
    n = _rng.normal(0, 1, len(t))
    y = _lowpass(n, 25) - _lowpass(n, 90)
    gurgle = 0.55 + 0.45 * np.sin(2 * np.pi * (11 + 6 * t) * t)
    return vel * 2.2 * np.sin(np.pi * t / 0.7) * gurgle * y


def twinkle(vel=1.0, notes=(100, 103, 96, 107, 103)):
    out = np.zeros(int(1.2 * SR))
    for i, m in enumerate(notes):
        g = glock(midi(m), 0.8, vel * 0.35)
        s = int(i * 0.055 * SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


def boop(vel=1.0):
    t = _t(0.25)
    f = 520 + 500 * (1 - np.exp(-t * 25))
    return vel * np.exp(-t * 12) * _attack(t, 2000) * np.sin(2 * np.pi * np.cumsum(f) / SR)


def snare_roll(dur=0.6, vel=1.0):
    out = np.zeros(int((dur + 0.2) * SR))
    t, gap = 0.0, 0.07
    while t < dur:
        tt = _t(0.06)
        hit = _rng.normal(0, 1, len(tt)) * np.exp(-tt * 60) * (0.4 + 0.6 * t / dur)
        s = int(t * SR)
        out[s:s + len(hit)] += hit
        t += gap
        gap = max(0.028, gap * 0.9)
    return vel * 0.35 * out


def wah_down(vel=1.0):
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate((67, 66, 65, 64)):
        d = 0.65 if i == 3 else 0.3
        t = _t(d)
        vib = 1 + (0.012 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0)
        f = midi(m - 12) * vib
        y = np.sin(2 * np.pi * np.cumsum(f) / SR)
        y = np.sign(y) * np.abs(y) ** 0.6  # a bit of horn-like buzz
        env = _attack(t, 200) * np.minimum(1, (d - t) / 0.08)
        s = int(i * 0.28 * SR)
        out[s:s + len(t)] += vel * 0.35 * env * y
    return out


def uh_oh(vel=1.0):
    out = np.zeros(int(0.9 * SR))
    for i, (m, d) in enumerate(((76, 0.2), (72, 0.45))):
        g = marimba(midi(m), d + 0.3, vel * 0.8)
        s = int(i * 0.22 * SR)
        out[s:s + len(g)] += g[:len(out) - s]
    return out


def jingle(mix, t, vel=1.0, ending=False):
    """The Snip & Crinkle signature: sol-mi-DO up (or DO-sol-DO for the ending)."""
    notes = (84, 79, 84) if ending else (79, 76, 84)
    for i, m in enumerate(notes):
        mix.add(t + i * 0.16, glock(midi(m), 1.1, 0.8 * vel))
        mix.add(t + i * 0.16, marimba(midi(m - 12), 0.6, 0.5 * vel))
    strum(mix, t + 0.32, "C", 0.9 * vel)
    mix.add(t + 0.32, bass(midi(36), 0.8, 0.9 * vel))


def reverb(y, wet=0.2, length=1.1, decay=4.5):
    t = np.arange(int(length * SR)) / SR
    ir = _rng.normal(0, 1, len(t)) * np.exp(-t * decay)
    ir = _lowpass(ir, 6)
    ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(y) + len(ir)
    size = 1 << (n - 1).bit_length()
    wet_sig = np.fft.irfft(np.fft.rfft(y, size) * np.fft.rfft(ir, size), size)[:len(y)]
    return (1 - wet) * y + wet * wet_sig * 0.5
