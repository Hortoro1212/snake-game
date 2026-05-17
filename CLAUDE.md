# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

```
python main.py
```

## Installing dependencies

Python 3.14 is in use. The standard `pygame` package does not have wheels for 3.14 — use `pygame-ce` (community edition) instead, which imports identically as `pygame`:

```
pip install -r requirements.txt
```

Sounds require `numpy`. If numpy is absent, `HAS_NUMPY` is `False` and sounds are silently skipped — the game is otherwise fully functional.

## Architecture

Everything lives in `main.py`. The game loop runs in `main()` and drives three states: `'menu'`, `'playing'`, `'game_over'`.

**Grid coordinate system** — all game logic uses `(col, row)` integer tuples on a 20×20 grid. `cell_rect(col, row)` converts to pixel space, accounting for the 40px HUD strip at the top (`HUD_H = 40`). Never pass pixel coordinates to game logic, and never pass grid coordinates to drawing functions directly.

**`Snake` class** (`main.py:115`) — the only stateful game object. `body` is a list of `(col, row)` tuples, head-first. `steer()` buffers the next direction in `_next` and applies it at the start of `step()`, preventing 180° reversal. `dead()` checks both wall collision and self-intersection. There is no wrap-around — walls are lethal.

**Food** — a single `(col, row)` tuple, not a class. `spawn_food(occupied)` picks randomly from the free cells each time food is eaten.

**Speed** — `current_speed(score)` returns FPS, scaling from `BASE_SPEED=8` to `MAX_SPEED=20`, increasing by 2 every `SPEEDUP_EVERY=5` points. The clock tick in the game loop is the only place this is applied.

**Sounds** — generated procedurally at startup via `make_tone()` using numpy sine waves with exponential decay. Stored as a `{'eat': Sound, 'die': Sound}` dict; `play(sounds, key)` is a null-safe wrapper. `pygame.mixer.pre_init()` must be called before `pygame.init()`, which is why it happens at the top of `main()`.

**High scores** — persisted to `highscores.json` alongside `main.py` (resolved via `__file__`). Top 5 scores, sorted descending. `hs_load()` / `hs_save(score)` handle all I/O; both swallow exceptions silently so a corrupt file never crashes the game.

**Drawing** — all `draw_*` functions take the pygame surface as their first argument. Overlay screens (menu, game over) call `draw_overlay()` to dim the game beneath them before rendering text. `blit_text()` uses a module-level `_fonts` dict to cache `SysFont` instances by size.

## Key constants to know when modifying

| Constant | Purpose |
|---|---|
| `CELL = 20` | Pixels per grid cell — changing this scales the entire game |
| `COLS / ROWS = 20` | Grid dimensions |
| `HUD_H = 40` | Height of the score bar; `cell_rect` adds this as a Y offset |
| `BASE_SPEED / MAX_SPEED` | FPS range for difficulty scaling |
| `SPEEDUP_EVERY` | Points between each speed increase |
