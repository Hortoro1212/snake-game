import random
import pygame
from settings import cfg

TYPES          = ['bonus', 'slow', 'shrink']
SPAWN_CHANCE   = 0.20
DURATION_MS    = 10_000   # power-up disappears after 10 s if uncollected


class PowerUp:
    def __init__(self, pos, kind):
        self.pos  = pos
        self.kind = kind
        self._born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self._born > DURATION_MS


def spawn_powerup(occupied):
    if random.random() > SPAWN_CHANCE:
        return None
    occupied_set = set(occupied)
    free = [
        (c, r)
        for c in range(cfg['cols'])
        for r in range(cfg['rows'])
        if (c, r) not in occupied_set
    ]
    if not free:
        return None
    return PowerUp(random.choice(free), random.choice(TYPES))


def apply_powerup(pu, snake, score, speed):
    """Return (new_score, new_speed, slow_activated)."""
    if pu.kind == 'bonus':
        return score + 3, speed, False
    if pu.kind == 'slow':
        return score, max(1, speed // 2), True
    if pu.kind == 'shrink':
        snake.shrink(3)
        return score, speed, False
    return score, speed, False
