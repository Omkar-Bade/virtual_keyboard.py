# smoother.py

class PositionSmoother:
    def __init__(self, alpha):
        self.alpha = alpha
        self.prev_x = 0
        self.prev_y = 0

    def smooth(self, x, y):
        sx = int(self.prev_x + self.alpha * (x - self.prev_x))
        sy = int(self.prev_y + self.alpha * (y - self.prev_y))

        self.prev_x, self.prev_y = sx, sy
        return sx, sy
