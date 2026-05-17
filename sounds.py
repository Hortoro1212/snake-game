import pygame

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


def _make_tone(freq, dur, vol=0.45, decay=35):
    sr = 44100
    t   = np.linspace(0, dur, int(sr * dur), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-decay * t) * vol
    pcm  = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([pcm, pcm]))


def init_sounds():
    if not _HAS_NUMPY:
        return {}
    try:
        return {
            'eat':      _make_tone(660, 0.07, decay=50),
            'die':      _make_tone(150, 0.45, vol=0.55, decay=4),
            'powerup':  _make_tone(880, 0.12, decay=30),
            'phase_up': _make_tone(440, 0.6,  vol=0.6,  decay=2),
        }
    except Exception:
        return {}


def play(sounds, key):
    s = sounds.get(key)
    if s:
        s.play()
