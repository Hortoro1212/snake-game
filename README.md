# Snake Game

A classic Snake game built with [pygame-ce](https://pyga.me/), featuring two phases, power-ups, 2-player mode, and procedurally generated sounds.

## Requirements

- Python 3.14+
- pygame-ce
- numpy (optional — enables procedural sound effects)

```
pip install -r requirements.txt
```

## Running

```
python main.py
```

## Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Move | Arrow keys | WASD |
| Pause | P | — |
| Menu navigation | Up / Down | — |

## Features

### Phase system

The game has two phases that automatically advance as you get faster:

| | Phase 0 | Phase 1 |
|---|---|---|
| Grid | 20×20 | 30×30 |
| Speed | 1–50 FPS | 50–100 FPS |
| Obstacles | None | Random wall segments |

### Power-ups

After each food item there is a 20% chance a power-up spawns (max 1 on screen, disappears after 10 s):

| Power-up | Effect |
|---|---|
| Bonus | +3 score |
| Slow | Halves speed for 5 seconds |
| Shrink | Removes 3 tail segments |

### 2-player mode

Select from the main menu. Both snakes share the same food and power-up pool. Cross-collision and head-on collision are both detected.

### High scores

Top 5 scores are saved to `highscores.json` alongside `main.py` and persist between sessions.
