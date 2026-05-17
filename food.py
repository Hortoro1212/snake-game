import random
from settings import cfg


def spawn_food(occupied):
    occupied_set = set(occupied)
    free = [
        (c, r)
        for c in range(cfg['cols'])
        for r in range(cfg['rows'])
        if (c, r) not in occupied_set
    ]
    return random.choice(free) if free else None
