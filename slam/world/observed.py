from typing import Dict, List, Tuple

import numpy as np

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.world.world as world


class ObservedWorld(world.World):
    def __init__(self):
        self.map: Dict[geometry.Point, List[datapoint.Observation]] = dict()
        self.last_prediction = None

    def add_observation(self, pose: datapoint.Pose,
                        observation: datapoint.Observation):
        if pose.location in self.map:
            self.map[pose.location].append(observation)
        else:
            self.map[pose.location] = [observation]

    def get_world_borders(self) -> Tuple[geometry.Point, geometry.Point]:
        if len(self.map) == 0:
            return None, None

        x_min, y_min = np.Inf, np.Inf
        x_max, y_max = np.NINF, np.NINF
        for observations in self.map.values():
            x_coords = [o.location.x for o in observations]
            x_min = min(x_min, min(x_coords))
            x_max = max(x_max, max(x_coords))

            y_coords = [o.location.y for o in observations]
            y_min = min(y_min, min(y_coords))
            y_max = max(y_max, max(y_coords))
        return (geometry.Point(x_min, y_min), geometry.Point(x_max, y_max))

    def predict_world(self) -> Tuple[List[List[int]], geometry.Point]:
        """
        Returns predited world and the origin of the world.
        """
        min_border, max_border = self.get_world_borders()
        if min_border is None or max_border is None:
            return (None, None)
        width = int(round(max_border.x - min_border.x)) + 1
        height = int(round(max_border.y - min_border.y)) + 1
        predicted = np.zeros([height, width])
        for observations in self.map.values():
            for obs in observations:
                x = obs.location.x - min_border.x
                y = obs.location.y - min_border.y
                predicted[int(round(y))][int(round(x))] = 1
        self.last_prediction = predicted
        return (predicted, min_border)

    def print(self):
        s = []
        for y in range(len(self.last_prediction) - 1, -1, -1):
            for x in range(len(self.last_prediction[y])):
                if self.last_prediction[y][x] > 0.5:
                    s.append("*")
                else:
                    s.append(".")
            s.append("\n")
        print(''.join(s))
