from typing import List, Tuple

import numpy as np

import slam.common.geometry as geometry
import slam.world.world as world


class SimulatedWorld(world.World):
    """
    World used for simulation.
    Obstacles format: (x_min, x_max, y_min, y_max)
    """
    def __init__(self, width=50, height=50, pose: geometry.Pose = None,
                 obstacles: List[Tuple[int]] = None):
        self.map = np.zeros([height, width])
        for obstacle in obstacles:
            x_min, x_max, y_min, y_max = obstacle
            self.map[y_min:y_max+1, x_min:x_max+1] = 1
        self.pose = pose

    def location_in_range(self, x: int, y: int) -> bool:
        return x >= 0 and x < self.map.shape[1] and \
            y >= 0 and y < self.map.shape[0]

    def update_pose(self, new_pose: geometry.Pose):
        self.pose = new_pose

    def get_distance_to_wall(self, measuring_angle: int) -> int:
        """
        Very imperfect.
        """
        angle = self.pose.orientation.in_degrees() + measuring_angle
        p = geometry.Pose(*self.pose.position, angle)
        distance = 0
        x = int(round(p.position.x))
        y = int(round(p.position.y))
        while self.location_in_range(x, y) and self.map[y][x] == 0:
            p.move_forward(1)
            distance += 1
            x = int(round(p.position.x))
            y = int(round(p.position.y))
        return distance


class PredefinedWorld(SimulatedWorld):
    """
    World with predefined obstacles.
    """
    def __init__(self, key: int):
        # Default
        w, h = 30, 50
        o = []
        p = geometry.Pose(5, 5, 90)

        if key == 1:
            w, h, = 40, 40
            o = [(0, 10, 20, 39)]
            p = geometry.Pose(5, 5, 0)
        elif key == 2:
            w, h = 30, 60
            o = [(15, 29, 20, 40)]
            p = geometry.Pose(20, 10, 0)
        elif key == 3:
            w, h = 50, 50
            o = [(20, 30, 20, 30)]
            p = geometry.Pose(40, 40, 180)
        elif key == 4:
            w, h = 50, 50
            o = [(0, 20, 20, 35), (40, 49, 0, 15)]
        elif key == 5:
            w, h = 50, 50
            o = [(0, 15, 20, 35), (30, 35, 0, 15)]
        elif key == 6:
            w, h = 60, 20
            o = [(20, 30, 0, 5)]
        elif key == 7:
            w, h = 110, 70
            o = [(40, 41, 0, 40), (75, 76, 30, 69)]
            p = geometry.Pose(20, 20, 0)

        super().__init__(width=w, height=h, pose=p, obstacles=o)
