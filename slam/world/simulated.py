import numpy as np

import slam.common.geometry as geometry
import slam.world.world as world


class SimulatedWorld(world.World):
    def __init__(self, pose: geometry.Pose = None):
        self.map = np.zeros([50, 50])
        for i in range(20):
            for j in range(10):
                self.map[i][j] = 1

        for i in range(30, 50):
            for j in range(20, 50):
                self.map[i][j] = 1

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
