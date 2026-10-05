"""Extra original instruments so each episode's story music has its own colour.

Rule (EPISODE_GUIDE "Music variety"): keep the signature jingle (start + paw-bump) and the
F -> G7 loop cadence exactly as they are, but give the story section of every episode its own
accompaniment instrument and lead. All sounds are synthesised here; no samples.

    import music_extra as MX
    MX.comp(music, t, "C", 0.6, inst="toy_piano")        # replaces A.strum for the story section
    music.add(t, MX.melodica(A.midi(72), 0.4, 0.6))       # lead voice
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import audio as A  # noqa: E402

SR = A.SR
_t = A._t

# chord tones (mid register); same names as audio.UKE_CHORDS so episode code can swap freely
CHORDS = {"C": (60, 64, 67, 72), "F": (60, 65, 69, 72), "G": (59, 62, 67, 71), "Am": (60, 64, 69, 72),
          "G7": (59, 62, 65, 67), "Dm": (62, 65, 69, 74), "Em": (59, 64, 67, 71), "Bb": (58, 62, 65, 70),
          "D7": (60, 62, 66, 69)}


def toy_piano(f, dur=0.8, vel=1.0):
    """Bright toy-piano tine: fundamental + inharmonic metal partials, quick decay."""
    t = _t(dur)
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t * 5.5)
         + 0.55 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 11)
         + 0.25 * np.sin(2 * np.pi * f * 5.43 * t) * np.exp(-t * 24)
         + 0.12 * np.sin(2 * np.pi * f * 7.9 * t) * np.exp(-t * 40))
    return vel * 0.7 * A._attack(t, 4000) * y


def melodica(f, dur=0.5, vel=1.0):
    """Reedy melodica: odd-heavy harmonics, gentle breath attack, light vibrato."""
    t = _t(dur)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.15)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    y = (np.sin(ph) + 0.55 * np.sin(3 * ph) + 0.3 * np.sin(2 * ph) + 0.22 * np.sin(5 * ph) + 0.1 * np.sin(7 * ph))
    env = np.minimum(1, t / 0.035) * np.minimum(1, (dur - t) / 0.06).clip(0, 1)
    return vel * 0.42 * env * y


def organ(f, dur=0.35, vel=1.0):
    """Bouncy toy organ: drawbar-style partials + a short key click; slightly detuned for warmth."""
    t = _t(dur)
    y = sum(a * (np.sin(2 * np.pi * f * r * t) + np.sin(2 * np.pi * f * r * 1.003 * t))
            for r, a in ((0.5, 0.35), (1, 1.0), (2, 0.6), (3, 0.3), (4, 0.18)))
    click = np.exp(-t * 900) * np.sin(2 * np.pi * 2400 * t) * 0.3
    env = np.minimum(1, t / 0.008) * np.minimum(1, (dur - t) / 0.05).clip(0, 1)
    return vel * 0.28 * (env * y + click)


def steel_pan(f, dur=0.9, vel=1.0):
    """Steel-drum-like bell: octave + twelfth partials with a soft 'ping'."""
    t = _t(dur)
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t * 4)
         + 0.5 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 6)
         + 0.25 * np.sin(2 * np.pi * f * 3.02 * t) * np.exp(-t * 9))
    return vel * 0.6 * A._attack(t, 1500) * y


INSTS = {"toy_piano": toy_piano, "organ": organ, "steel_pan": steel_pan, "melodica": melodica}


def comp(mix, t, chord, vel=1.0, up=False, inst="toy_piano", gain=1.0):
    """Drop-in replacement for audio.strum: a chord on another instrument.
    `up` = a quick rolled arpeggio (like an up-strum), otherwise a block chord."""
    voice = INSTS[inst]
    notes = CHORDS[chord]
    for i, m in enumerate(reversed(notes) if up else notes):
        dt = i * (0.045 if up else 0.006)
        mix.add(t + dt, voice(A.midi(m), 0.7 if inst != "organ" else 0.3, vel * (0.75 if up else 0.85)), gain)
