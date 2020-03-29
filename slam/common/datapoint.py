from __future__ import annotations

import slam.common.enums as enums
import slam.common.geometry as geometry


class DataPoint():
    def __init__(self, x, y):
        self.location = geometry.Point(x, y)
        self.color = (0., 0., 0., 0.3)
        self.graph_type = enums.GraphType.SCATTER

    def __eq__(self, other: DataPoint):
        return self.location == other.location and \
            self.graph_type == other.graph_type

    def __str__(self):
        return f"{self.location}, {self.graph_type.name=}"


class Observation(DataPoint):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (0.1, 0.2, 0.9, 0.3)


class Pose(DataPoint):
    def __init__(self, x, y, angle):
        super().__init__(x, y)
        self.angle = geometry.Angle(angle)
        self.color = (0.9, 0.2, 0.1, 0.3)


class Prediction(DataPoint):
    """
    (x, y) are coordinates of the origin of the world
    """
    def __init__(self, x, y, predicted_world):
        super().__init__(x, y)
        self.graph_type = enums.GraphType.HEATMAP
        self.predicted_world = predicted_world
