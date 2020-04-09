from __future__ import annotations

from typing import List

import slam.common.enums as enums
import slam.common.geometry as geometry
from slam.common.enums import Existence, ObservationType


class DataPoint():
    def __init__(self, x, y, color=None, path_id: int = None,
                 path_style: str = "-",
                 existence: Existence = Existence.PERMANENT):
        self.location = geometry.Point(x, y)
        self.color = color if color is not None else (0., 0., 0., 0.3)
        self.graph_type = enums.GraphType.SCATTER
        self.path_id = path_id
        self.path_style = path_style
        self.existence = existence

    def __eq__(self, other: DataPoint):
        return self.location == other.location and \
            self.graph_type == other.graph_type

    def __str__(self):
        return f"{self.location}, {self.graph_type.name=}"

    def __getitem__(self, key) -> DataPoint:
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key == 0:
            return self
        raise IndexError("Only index 0 is accepted")


class Observation(DataPoint):
    def __init__(self, x, y, otype: ObservationType):
        if otype == ObservationType.OBSTACLE:
            c = (0.1, 0.2, 0.9, 0.3)
        elif otype == ObservationType.FREE:
            c = (0.4, 1.0, 0.1, 0.3)
        super().__init__(x, y, color=c)
        self.type = otype


class Pose(DataPoint):
    def __init__(self, x, y, angle, path_id: int = None):
        c = (0.9, 0.2, 0.1, 0.3)
        super().__init__(x, y, color=c, path_id=path_id)
        self.angle = geometry.Angle(angle)


class Prediction(DataPoint):
    """
    (x, y) are coordinates of the origin of the world
    """
    def __init__(self, x, y, predicted_world):
        super().__init__(x, y)
        self.graph_type = enums.GraphType.HEATMAP
        self.predicted_world = predicted_world


class Frontier(DataPoint):
    """
    (x, y) are coordinates of the origin of the world
    """
    def __init__(self, x, y, frontier: List[geometry.Point]):
        c = (0.1, 0.5, 0.1, 0.3)
        super().__init__(x, y, color=c, existence=Existence.TEMPORARY)
        self.frontier = frontier

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key >= 0 and key < len(self.frontier):
            return DataPoint(*self.frontier[key], color=self.color,
                             existence=self.existence)
        raise IndexError(f"Key {key} out of range for array of length "
                         f"{len(self.frontier)}")

    def __len__(self):
        return len(self.frontier)
