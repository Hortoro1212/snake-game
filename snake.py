from settings import cfg


class Snake:
    def __init__(self, start_col=None, start_row=None, direction=(1, 0)):
        if start_col is None:
            start_col = cfg['cols'] // 2
        if start_row is None:
            start_row = cfg['rows'] // 2
        dx, dy = direction
        self.body = [
            (start_col,          start_row),
            (start_col - dx,     start_row - dy),
            (start_col - dx * 2, start_row - dy * 2),
        ]
        self.dir   = direction
        self._next = direction
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

    def shrink(self, n=3):
        for _ in range(n):
            if len(self.body) > 1:
                self.body.pop()

    @property
    def head(self):
        return self.body[0]

    def dead(self, obstacles=None):
        hx, hy = self.head
        out      = hx < 0 or hx >= cfg['cols'] or hy < 0 or hy >= cfg['rows']
        self_hit = self.head in self.body[1:]
        obs_hit  = bool(obstacles and self.head in obstacles)
        return out or self_hit or obs_hit
