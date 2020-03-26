from __future__ import annotations

import slam.common.geometry as geometry


class DataPoint():
    def __init__(self, x, y):
        self.location = geometry.Point(x, y)
        self.color = (0., 0., 0., 0.3)

    def __eq__(self, other: DataPoint):
        return self.location == other.location


class Observation(DataPoint):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0.1, 0.2, 0.9, 0.3)


class Position(DataPoint):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0.9, 0.2, 0.1, 0.3)
