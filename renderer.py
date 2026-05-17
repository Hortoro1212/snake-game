import pygame
from settings import (
    cfg,
    BG, GRID_C,
    SH, SB, SO,
    FC, FH, FST,
    PU_BONUS, PU_SLOW, PU_SHRINK,
    OBS_C, OBS_HL,
    HUD_BG,
    C_GOLD, C_WHITE, C_GREEN, C_RED, C_BLUE,
)

_fonts = {}


def clear_font_cache():
    _fonts.clear()


def _font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("Courier New", size, bold=True)
    return _fonts[size]


def _text(surf, text, size, color, cx, cy):
    s = _font(size).render(text, False, color)
    surf.blit(s, s.get_rect(center=(cx, cy)))


def cell_rect(col, row):
    cell = cfg['cell']
    return pygame.Rect(col * cell, cfg['hud_h'] + row * cell, cell, cell)


# ── Core game objects ────────────────────────────────────────────────────────

def draw_grid(surf):
    for c in range(cfg['cols']):
        for r in range(cfg['rows']):
            pygame.draw.rect(surf, GRID_C, cell_rect(c, r), 1)


def draw_snake(surf, snake, head_color=SH, body_color=SB, outline_color=SO):
    for i, (c, r) in enumerate(snake.body):
        rect  = cell_rect(c, r)
        color = head_color if i == 0 else body_color
        pygame.draw.rect(surf, outline_color, rect)
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
            pygame.draw.circle(surf, outline_color, e1, 2)
            pygame.draw.circle(surf, outline_color, e2, 2)


def draw_food(surf, pos):
    if pos is None:
        return
    r = cell_rect(*pos).inflate(-4, -4)
    pygame.draw.rect(surf, FC, r)
    pygame.draw.rect(surf, FH, pygame.Rect(r.x + 2, r.y + 2, 3, 3))
    pygame.draw.rect(surf, FST, pygame.Rect(r.centerx - 1, r.top - 3, 2, 4))


def draw_powerup(surf, pu):
    color_map = {'bonus': PU_BONUS, 'slow': PU_SLOW, 'shrink': PU_SHRINK}
    color = color_map.get(pu.kind, C_GOLD)
    r = cell_rect(*pu.pos)
    # Pulsing outline
    pulse = abs(pygame.time.get_ticks() % 800 - 400) / 400
    border = tuple(int(c * (0.4 + 0.6 * pulse)) for c in color)
    pygame.draw.rect(surf, border, r, 2)
    inner = r.inflate(-4, -4)
    pygame.draw.rect(surf, color, inner)
    label = {'bonus': 'B', 'slow': 'S', 'shrink': '-'}.get(pu.kind, '?')
    s = _font(max(9, cfg['cell'] - 10)).render(label, False, (0, 0, 0))
    surf.blit(s, s.get_rect(center=inner.center))


def draw_obstacles(surf, obstacles):
    for c, r in obstacles:
        rect = cell_rect(c, r)
        pygame.draw.rect(surf, OBS_C, rect)
        pygame.draw.rect(surf, OBS_HL, rect, 1)


# ── HUD ─────────────────────────────────────────────────────────────────────

def draw_hud(surf, score, speed, best, mode='1p', score2=None, user=None):
    w   = cfg['win_w']
    h   = cfg['hud_h']
    fs  = 12 if w <= 400 else 14
    mid = h // 2
    pygame.draw.rect(surf, HUD_BG, (0, 0, w, h))
    pygame.draw.line(surf, GRID_C, (0, h - 1), (w, h - 1))
    if mode == '2p' and score2 is not None:
        _text(surf, f"P1 {score:03d}",  fs, C_GREEN, w // 5,      mid)
        _text(surf, f"SPD {speed:02d}", fs, C_GOLD,  w // 2,      mid)
        _text(surf, f"P2 {score2:03d}", fs, C_BLUE,  w * 4 // 5,  mid)
    else:
        _text(surf, f"SCR {score:04d}", fs, C_GOLD,  w // 5,      mid)
        _text(surf, f"SPD {speed:02d}", fs, C_WHITE, w // 2,      mid)
        if user:
            display = user if len(user) <= 10 else user[:9] + '~'
            _text(surf, display,            fs, C_BLUE,  w * 4 // 5, mid)
        else:
            _text(surf, f"BST {best:04d}", fs, C_WHITE, w * 4 // 5, mid)


# ── Overlays ─────────────────────────────────────────────────────────────────

def _overlay(surf, alpha=170):
    s = pygame.Surface((cfg['win_w'], cfg['win_h']), pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    surf.blit(s, (0, 0))


def draw_menu(surf, scores, selected_mode):
    _overlay(surf, 185)
    mid = cfg['win_w'] // 2
    h   = cfg['win_h']
    _text(surf, "SNAKE",         52, C_GREEN, mid, h // 5)
    _text(surf, "RETRO EDITION", 14, C_GOLD,  mid, h // 5 + 52)

    for i, (label, mode) in enumerate([("1 PLAYER", '1p'), ("2 PLAYERS", '2p')]):
        color  = C_GREEN if selected_mode == mode else C_WHITE
        prefix = ">>" if selected_mode == mode else "  "
        _text(surf, f"{prefix} {label} {prefix}", 16, color, mid, h // 2 - 15 + i * 30)

    _text(surf, "-- HIGH SCORES --", 13, C_WHITE, mid, h // 2 + 65)
    for i, s in enumerate(scores[:5]):
        _text(surf, f"{i + 1}.  {s:04d}", 13, C_GOLD, mid, h // 2 + 85 + i * 19)

    _text(surf, "UP/DOWN  choose mode", 11, C_WHITE, mid, h - 48)
    _text(surf, "SPACE  start",         14, C_GREEN, mid, h - 28)


def draw_pause(surf):
    _overlay(surf, 150)
    mid  = cfg['win_w'] // 2
    midy = cfg['win_h'] // 2
    _text(surf, "PAUSED",     42, C_WHITE, mid, midy - 30)
    _text(surf, "P   resume", 14, C_WHITE, mid, midy + 28)
    _text(surf, "ESC quit",   14, C_WHITE, mid, midy + 52)


def draw_gameover(surf, score, score2, new_best, winner=None):
    _overlay(surf, 160)
    mid  = cfg['win_w'] // 2
    midy = cfg['win_h'] // 2
    if winner == 0:
        _text(surf, "DRAW!",  40, C_GOLD, mid, midy - 70)
        _text(surf, f"P1 {score:04d}   P2 {score2:04d}", 18, C_WHITE, mid, midy - 15)
    elif winner in (1, 2):
        color = C_GREEN if winner == 1 else C_BLUE
        _text(surf, f"PLAYER {winner} WINS!", 36, color, mid, midy - 70)
        _text(surf, f"P1 {score:04d}   P2 {score2:04d}", 18, C_WHITE, mid, midy - 15)
    else:
        _text(surf, "GAME OVER",        40, C_RED,  mid, midy - 70)
        _text(surf, f"SCORE:  {score:04d}", 22, C_GOLD, mid, midy - 15)
    if new_best:
        _text(surf, "** NEW BEST **", 17, C_GREEN, mid, midy + 25)
    _text(surf, "SPACE  -  play again", 13, C_WHITE, mid, midy + 68)
    _text(surf, "ESCAPE -  quit",       13, C_WHITE, mid, midy + 90)


def draw_phase_transition(surf, phase_num):
    _overlay(surf, 200)
    mid  = cfg['win_w'] // 2
    midy = cfg['win_h'] // 2
    _text(surf, f"PHASE {phase_num}",             50, C_GOLD,  mid, midy - 60)
    _text(surf, "BOARD EXPANDED",                 22, C_GREEN, mid, midy +  5)
    _text(surf, "OBSTACLES INCOMING...",           15, C_RED,   mid, midy + 38)
    _text(surf, "MAX SPEED NOW 100",               13, C_WHITE, mid, midy + 62)


def draw_login(surf, email_input, cursor_visible, error_msg=None):
    _overlay(surf, 220)
    mid = cfg['win_w'] // 2
    h   = cfg['win_h']

    _text(surf, "SNAKE",         52, C_GREEN, mid, h // 5)
    _text(surf, "RETRO EDITION", 14, C_GOLD,  mid, h // 5 + 52)
    _text(surf, "SIGN IN TO PLAY", 16, C_WHITE, mid, h // 2 - 60)

    box_w  = cfg['win_w'] - 60
    box_x  = 30
    box_y  = h // 2 - 15
    box_rect = pygame.Rect(box_x, box_y, box_w, 30)
    pygame.draw.rect(surf, (30, 45, 30), box_rect)
    pygame.draw.rect(surf, C_GREEN, box_rect, 1)

    display = email_input + ('|' if cursor_visible else ' ')
    surf.blit(_font(13).render(display, False, C_GOLD), (box_x + 6, box_y + 7))

    if error_msg:
        _text(surf, error_msg, 12, C_RED, mid, h // 2 + 30)

    _text(surf, "TYPE EMAIL  THEN  ENTER", 11, C_WHITE, mid, h - 48)
    _text(surf, "ESC  quit",               11, C_WHITE, mid, h - 28)


def draw_awaiting_auth(surf, email):
    _overlay(surf, 220)
    mid = cfg['win_w'] // 2
    h   = cfg['win_h']

    _text(surf, "MAGIC LINK SENT", 30, C_GREEN, mid, h // 4)

    pulse = abs(pygame.time.get_ticks() % 1200 - 600) / 600
    brightness = int(100 + 100 * pulse)
    _text(surf, "[ @ ]", 36, (brightness, brightness, brightness), mid, h // 2 - 20)

    _text(surf, "CHECK YOUR INBOX", 14, C_WHITE, mid, h // 2 + 30)
    shown = email if len(email) <= 28 else email[:26] + '..'
    _text(surf, shown,             12, C_GOLD,  mid, h // 2 + 55)

    _text(surf, "CLICK THE LINK IN YOUR EMAIL", 11, C_WHITE, mid, h - 65)
    _text(surf, "THEN RETURN HERE",             11, C_WHITE, mid, h - 45)
    _text(surf, "ESC  cancel",                  11, C_WHITE, mid, h - 25)
