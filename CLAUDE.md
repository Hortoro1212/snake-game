# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```
python main.py
```

## Installing dependencies

Python 3.14 is in use. Use `pygame-ce` (community edition) — the standard `pygame` package has no 3.14 wheels. Both import as `pygame`.

```
pip install -r requirements.txt
```

Sounds require `numpy`. If absent, sounds are silently skipped; everything else works normally.

## Architecture

### File map

| File | Responsibility |
|---|---|
| `settings.py` | `PHASES` list, mutable `cfg` dict, all color constants |
| `snake.py` | `Snake` class |
| `food.py` | `spawn_food()` |
| `powerups.py` | `PowerUp` class, `spawn_powerup()`, `apply_powerup()` |
| `obstacles.py` | `generate_obstacles()` — empty in phase 0, wall segments in phase 1+ |
| `sounds.py` | Procedural tone generation, `init_sounds()`, `play()` |
| `highscore.py` | JSON persistence, `hs_load()` / `hs_save()` |
| `renderer.py` | All `draw_*` functions, `cell_rect()`, font cache |
| `main.py` | pygame init, game loop, event dispatch, state machine |

### Shared mutable config (`settings.cfg`)

All modules import `cfg` from `settings`. On phase transition, `cfg` is updated **in-place** via `cfg.update(...)` so every module immediately sees the new board dimensions, speed caps, etc. Never copy individual values out of `cfg` into local module-level variables — they won't update.

### Grid coordinate system

All game logic uses `(col, row)` integer tuples. `renderer.cell_rect(col, row)` converts to pixel space, adding `cfg['hud_h']` (40 px) as a Y offset for the HUD bar. Never pass pixel coordinates to game logic.

### Phase system

| | Phase 0 | Phase 1 |
|---|---|---|
| Grid | 20×20, 20 px/cell, 400×440 window | 30×30, 25 px/cell, 750×790 window |
| Speed | 1–50 FPS | 50–100 FPS |
| Obstacles | None | ~12 random wall segments |

Phase transition triggers in `main.py` when `speed >= cfg['max_speed']` and `phase_idx == 0`. At that point: `cfg.update(PHASES[1])`, `pygame.display.set_mode()` returns a new surface (reassign `screen`), snakes and food reset to the new board, `renderer.clear_font_cache()` is called. A 2.5-second announcement screen (`state = 'phase_transition'`) plays before gameplay resumes.

### State machine (`main.py`)

States: `'menu'` → `'playing'` ↔ `'paused'` → `'game_over'` → reset to `'playing'`.  
`'phase_transition'` auto-advances to `'playing'` after `TRANSITION_MS` ms.

### Speed

`speed` is an explicit integer variable in `main.py` (not derived from score). It starts at `cfg['base_speed']` (1) and increments by `cfg['speed_increment']` (5) every `cfg['speedup_every']` (5) food items eaten. Speed increases are skipped while the slow power-up is active. `speed` is passed directly to `clock.tick(speed)` so it is literally the game FPS.

### `Snake` class (`snake.py`)

`body` is a list of `(col, row)` tuples, head-first. `steer()` buffers next direction in `_next` to prevent 180° reversal. `dead(obstacles)` checks walls, self-collision, and obstacle set. `shrink(n)` removes up to n tail segments (used by shrink power-up).

### Power-ups (`powerups.py`)

Three types — `'bonus'` (+3 score), `'slow'` (halves speed for 5 s, restored in main loop when `slow_end` timestamp passes), `'shrink'` (removes 3 tail segments). 20% spawn chance after each food item. Max 1 on screen. Disappears after 10 s if uncollected.

### 2-player mode

Menu UP/DOWN switches between 1P and 2P. In 2P: Player 1 = arrow keys (green snake), Player 2 = WASD (blue snake). Both snakes share the same food and power-up pool. Cross-collision and head-on collision are both detected. Winner determined by `winner` variable: `None` = 1P death, `0` = draw, `1`/`2` = that player won.

### Key constants to tune

| Location | Key | Effect |
|---|---|---|
| `settings.PHASES[0]` | `base_speed` | Starting FPS (currently 5) |
| `settings.PHASES[0]` | `speed_increment` | FPS added per food eaten (currently 5) |
| `settings.PHASES[0]` | `speedup_every` | Food items between speed bumps (currently 1 = every food) |
| `settings.PHASES[0/1]` | `max_speed` | Phase speed cap (50 / 100) |
| `main.N_OBSTACLES` | — | Wall segment count spawned in phase 2 |
| `main.TRANSITION_MS` | — | Phase announcement duration ms |
| `main.SLOW_MS` | — | Slow power-up duration ms |
| `powerups.SPAWN_CHANCE` | — | Probability of power-up after food (0.0–1.0) |
