#!/usr/bin/env python3
"""Snake - Retro Pixel Art Edition"""

import pygame
import sys
import json
import os
import random

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# ── Layout ──────────────────────────────────────────────────────────────────
CELL   = 20
COLS   = 20
ROWS   = 20
HUD_H  = 40
WIN_W  = COLS * CELL          # 400
WIN_H  = ROWS * CELL + HUD_H  # 440

BASE_SPEED    = 8
MAX_SPEED     = 20
SPEEDUP_EVERY = 5   # +2 fps per N points

HIGHSCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")

# ── Palette ─────────────────────────────────────────────────────────────────
BG      = (12,  18,  12)
GRID_C  = (20,  30,  20)
SH      = (60,  220, 60)    # snake head
SB      = (35,  175, 35)    # snake body
SO      = (8,   80,  8)     # snake outline / eyes
FC      = (210, 55,  55)    # food body
FH      = (245, 135, 135)   # food highlight
FST     = (90,  55,  10)    # food stem
HUD_BG  = (8,   12,  8)
C_GOLD  = (255, 210, 60)
C_WHITE = (200, 200, 200)
C_GREEN = (60,  230, 80)
C_RED   = (255, 70,  70)


# ── Helpers ─────────────────────────────────────────────────────────────────
def cell_rect(col, row):
    return pygame.Rect(col * CELL, HUD_H + row * CELL, CELL, CELL)


_fonts = {}
def get_font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Courier New", size, bold=True)
    return _fonts[size]


def blit_text(surf, text, size, color, cx, cy):
    s = get_font(size).render(text, False, color)
    surf.blit(s, s.get_rect(center=(cx, cy)))


# ── Sound ────────────────────────────────────────────────────────────────────
def make_tone(freq, dur, vol=0.45, decay=35):
    sr = 44100
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    wave = np.sin(2 * np.pi * freq * t) * np.exp(-decay * t) * vol
    pcm = np.clip(wave * 32767, -32768, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([pcm, pcm]))


def init_sounds():
    if not HAS_NUMPY:
        return {}
    try:
        return {
            'eat': make_tone(660, 0.07, decay=50),
            'die': make_tone(150, 0.45, vol=0.55, decay=4),
        }
    except Exception:
        return {}


def play(sounds, key):
    s = sounds.get(key)
    if s:
        s.play()


# ── High Scores ──────────────────────────────────────────────────────────────
def hs_load():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return []


def hs_save(score):
    scores = hs_load()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:5]
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(scores, f)
    except Exception:
        pass
    return scores


# ── Snake ───────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body  = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.dir   = (1, 0)
        self._next = (1, 0)
        self._grow = False

    def steer(self, dx, dy):
        if (dx, dy) != (-self.dir[0], -self.dir[1]):
            self._next = (dx, dy)

    def step(self):
        self.dir = self._next
        hx, hy = self.body[0]
        dx, dy = self.dir
        self.body.insert(0, (hx + dx, hy + dy))
        if self._grow:
            self._grow = False
        else:
            self.body.pop()

    def eat(self):
        self._grow = True

    @property
    def head(self):
        return self.body[0]

    def dead(self):
        hx, hy = self.head
        return hx < 0 or hx >= COLS or hy < 0 or hy >= ROWS or self.head in self.body[1:]


# ── Food ────────────────────────────────────────────────────────────────────
def spawn_food(occupied):
    occupied_set = set(occupied)
    free = [(c, r) for c in range(COLS) for r in range(ROWS) if (c, r) not in occupied_set]
    return random.choice(free) if free else None


# ── Drawing ─────────────────────────────────────────────────────────────────
def draw_grid(surf):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(surf, GRID_C, cell_rect(c, r), 1)


def draw_snake(surf, snake):
    for i, (c, r) in enumerate(snake.body):
        rect  = cell_rect(c, r)
        color = SH if i == 0 else SB
        pygame.draw.rect(surf, SO, rect)
        pygame.draw.rect(surf, color, rect.inflate(-2, -2))

        if i == 0:
            dx, dy = snake.dir
            ex, ey = rect.centerx, rect.centery
            if dx != 0:
                e1 = (ex + dx * 4, ey - 3)
                e2 = (ex + dx * 4, ey + 3)
            else:
                e1 = (ex - 3, ey + dy * 4)
                e2 = (ex + 3, ey + dy * 4)
            pygame.draw.circle(surf, SO, e1, 2)
            pygame.draw.circle(surf, SO, e2, 2)


def draw_food(surf, pos):
    if pos is None:
        return
    r = cell_rect(*pos).inflate(-4, -4)
    pygame.draw.rect(surf, FC, r)
    pygame.draw.rect(surf, FH, pygame.Rect(r.x + 2, r.y + 2, 3, 3))
    # Stem above food body
    pygame.draw.rect(surf, FST, pygame.Rect(r.centerx - 1, r.top - 3, 2, 4))


def draw_hud(surf, score, best):
    pygame.draw.rect(surf, HUD_BG, (0, 0, WIN_W, HUD_H))
    pygame.draw.line(surf, GRID_C, (0, HUD_H - 1), (WIN_W, HUD_H - 1))
    blit_text(surf, f"SCORE  {score:04d}", 14, C_GOLD,  WIN_W // 4,     HUD_H // 2)
    blit_text(surf, f"BEST   {best:04d}",  14, C_WHITE, WIN_W * 3 // 4, HUD_H // 2)


def draw_overlay(surf, alpha=170):
    s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surf.blit(s, (0, 0))


def draw_menu(surf, scores):
    draw_overlay(surf, 185)
    mid = WIN_W // 2
    blit_text(surf, "SNAKE",           52, C_GREEN, mid, 145)
    blit_text(surf, "RETRO EDITION",   14, C_GOLD,  mid, 193)
    blit_text(surf, "-- HIGH SCORES --",13, C_WHITE, mid, 248)
    for i, s in enumerate(scores[:5]):
        blit_text(surf, f"{i + 1}.  {s:04d}", 13, C_GOLD, mid, 268 + i * 19)
    blit_text(surf, "PRESS SPACE TO PLAY",  14, C_GREEN, mid, 390)
    blit_text(surf, "ARROWS / WASD to move", 11, C_WHITE, mid, 414)


def draw_gameover(surf, score, new_best):
    draw_overlay(surf, 160)
    mid = WIN_W // 2
    blit_text(surf, "GAME OVER",         40, C_RED,   mid, 210)
    blit_text(surf, f"SCORE:  {score:04d}", 22, C_GOLD, mid, 268)
    if new_best:
        blit_text(surf, "** NEW BEST **",  17, C_GREEN, mid, 304)
    blit_text(surf, "SPACE  -  play again", 13, C_WHITE, mid, 368)
    blit_text(surf, "ESCAPE -  quit",       13, C_WHITE, mid, 390)


# ── Speed ───────────────────────────────────────────────────────────────────
def current_speed(score):
    return min(BASE_SPEED + (score // SPEEDUP_EVERY) * 2, MAX_SPEED)


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    if HAS_NUMPY:
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
        except Exception:
            pass

    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake - Retro Edition")
    clock  = pygame.time.Clock()
    sounds = init_sounds()

    scores   = hs_load()
    best     = scores[0] if scores else 0
    snake    = Snake()
    food     = spawn_food(snake.body)
    score    = 0
    new_best = False
    state    = 'menu'

    def reset():
        nonlocal snake, food, score, new_best
        snake    = Snake()
        food     = spawn_food(snake.body)
        score    = 0
        new_best = False

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if ev.type == pygame.KEYDOWN:
                if state == 'playing':
                    if   ev.key in (pygame.K_UP,    pygame.K_w): snake.steer( 0, -1)
                    elif ev.key in (pygame.K_DOWN,  pygame.K_s): snake.steer( 0,  1)
                    elif ev.key in (pygame.K_LEFT,  pygame.K_a): snake.steer(-1,  0)
                    elif ev.key in (pygame.K_RIGHT, pygame.K_d): snake.steer( 1,  0)
                    elif ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                elif state in ('menu', 'game_over'):
                    if ev.key == pygame.K_SPACE:
                        reset()
                        state = 'playing'
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

        if state == 'playing':
            snake.step()
            if snake.dead():
                play(sounds, 'die')
                scores   = hs_save(score)
                best     = scores[0] if scores else 0
                new_best = score > 0 and score == best
                state    = 'game_over'
            elif snake.head == food:
                score += 1
                snake.eat()
                food = spawn_food(snake.body)
                play(sounds, 'eat')

        screen.fill(BG)
        draw_grid(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)
        draw_hud(screen, score, best)

        if state == 'menu':
            draw_menu(screen, scores)
        elif state == 'game_over':
            draw_gameover(screen, score, new_best)

        pygame.display.flip()
        clock.tick(current_speed(score) if state == 'playing' else 30)


if __name__ == '__main__':
    main()
