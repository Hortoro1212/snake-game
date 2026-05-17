HUD_H = 40

PHASES = [
    {
        'phase': 0,
        'cols': 20, 'rows': 20, 'cell': 20,
        'win_w': 400, 'win_h': 440,
        'base_speed': 5, 'max_speed': 50,
        'speed_increment': 1, 'speedup_every': 1,
    },
    {
        'phase': 1,
        'cols': 30, 'rows': 30, 'cell': 25,
        'win_w': 750, 'win_h': 790,
        'base_speed': 50, 'max_speed': 100,
        'speed_increment': 1, 'speedup_every': 1,
    },
]

# Mutated in-place on phase transition — all modules import this dict
cfg = {**PHASES[0], 'hud_h': HUD_H}

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = (12,  18,  12)
GRID_C   = (20,  30,  20)
SH       = (60,  220, 60)    # snake 1 head
SB       = (35,  175, 35)    # snake 1 body
SO       = (8,   80,  8)     # snake 1 outline / eyes
SH2      = (60,  140, 220)   # snake 2 head
SB2      = (35,  100, 175)   # snake 2 body
SO2      = (8,   50,  100)   # snake 2 outline / eyes
FC       = (210, 55,  55)    # food body
FH       = (245, 135, 135)   # food highlight
FST      = (90,  55,  10)    # food stem
PU_BONUS  = (255, 215, 0)    # power-up: bonus points (gold)
PU_SLOW   = (100, 180, 255)  # power-up: slow (light blue)
PU_SHRINK = (220, 100, 255)  # power-up: shrink (purple)
OBS_C    = (90,  90,  100)   # obstacle fill
OBS_HL   = (120, 120, 135)   # obstacle highlight edge
HUD_BG   = (8,   12,  8)
C_GOLD   = (255, 210, 60)
C_WHITE  = (200, 200, 200)
C_GREEN  = (60,  230, 80)
C_RED    = (255, 70,  70)
C_BLUE   = (60,  160, 255)
