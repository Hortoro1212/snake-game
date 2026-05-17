import random
from settings import cfg

_MARGIN = 2


def generate_obstacles(n_segments, protected):
    """Return a set of (col, row) wall cells for the current phase.
    Phase 0 always returns an empty set.
    Each segment is 2-4 cells long in a random axis-aligned direction."""
    if cfg['phase'] == 0:
        return set()

    walls    = set()
    attempts = 0

    while len(walls) < n_segments * 2 and attempts < n_segments * 30:
        attempts += 1
        c = random.randint(_MARGIN, cfg['cols'] - _MARGIN - 1)
        r = random.randint(_MARGIN, cfg['rows'] - _MARGIN - 1)
        dc, dr = random.choice([(1, 0), (0, 1)])
        length = random.randint(2, 4)
        segment = set()
        for i in range(length):
            nc, nr = c + dc * i, r + dr * i
            if _MARGIN <= nc < cfg['cols'] - _MARGIN and _MARGIN <= nr < cfg['rows'] - _MARGIN:
                if (nc, nr) not in protected:
                    segment.add((nc, nr))
        walls |= segment

    return walls
