import random
from typing import Callable, Dict, List, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.world.world as world


def get_obstacle_filter(size: int = 7, sigma: float = 2.) -> np.ndarray:

    kernel = np.zeros([size, size])
    kernel[size//2][size//2] = 1
    kernel = 100 * gaussian_filter(kernel, sigma=sigma)
    return kernel


def apply_filter_on_coordinate(grid: np.ndarray, x_center: int,
                               y_center: int, kernel: np.ndarray,
                               f: Callable[[float, float], float] = sum) \
        -> np.ndarray:
    """
    Apply kernel with function f on grid with the center of kernel placed on
    (x_center, y_center).
    """

    filter_sizey, filter_sizex = kernel.shape
    for yi in range(filter_sizey):
        for xi in range(filter_sizex):
            x = x_center - int(filter_sizex//2) + xi
            y = y_center - int(filter_sizey//2) + yi
            if y >= 0 and y < len(grid) and x >= 0 and x < len(grid[y]):
                grid[y][x] = f([grid[y][x], kernel[yi][xi]])
    return grid


def apply_function_on_path(grid: np.ndarray, x_start: int, y_start: int,
                           x_end: int, y_end: int,
                           f: Callable[[float], float]) -> np.ndarray:
    """
    Apply function f on the path from (x_start, y_start) to (x_end, y_end).
    """
    p = geometry.Pose(x_start, y_start)
    p_end = geometry.Point(x_end, y_end)
    p.turn_towards(p_end)
    x_old = x_start
    y_old = y_start

    while p.position.distance_to(p_end) > 0.5:
        x = int(round(p.position.x))
        y = int(round(p.position.y))
        p.move_forward(1)

        if x == x_old and y == y_old:
            continue

        grid[y][x] = f(grid[y][x])

        x_old = x
        y_old = y
    return grid


class DictEntry():
    def __init__(self, observations: List[datapoint.Observation]):
        self.observations = observations
        self.used_in_prediction = False

    def __getitem__(self, key: int):
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key >= 0 and key < len(self.observations):
            return self.observations[key]
        raise IndexError(f"Key {key} out of range for array of length "
                         f"{len(self.observations)}")


class ObservedWorld(world.World):
    def __init__(self):
        self.map: Dict[geometry.Point, DictEntry] = dict()
        self.last_prediction = None
        self.last_prediction_blurred = None

    def add_observation(self, pose: datapoint.Pose,
                        observation: datapoint.Observation):
        if pose.location in self.map:
            self.map[pose.location].observations.append(observation)
        else:
            self.map[pose.location] = DictEntry([observation])

    def get_world_borders(self) -> Tuple[geometry.Point, geometry.Point]:
        if len(self.map) == 0:
            return None, None

        x_min, y_min = np.Inf, np.Inf
        x_max, y_max = np.NINF, np.NINF
        for entry in self.map.values():
            x_coords = [o.location.x for o in entry]
            x_min = min(x_min, min(x_coords))
            x_max = max(x_max, max(x_coords))

            y_coords = [o.location.y for o in entry]
            y_min = min(y_min, min(y_coords))
            y_max = max(y_max, max(y_coords))
        return (geometry.Point(x_min, y_min), geometry.Point(x_max, y_max))

    def point_in_bounds(self, point: geometry.Point) -> bool:
        min_border, max_border = self.get_world_borders()
        return min_border.x <= point.x <= max_border.x and \
            min_border.y <= point.y <= max_border.y

    def predict_world(self, sigma: int = 1) \
            -> Tuple[np.ndarray, geometry.Point]:
        """
        Returns predited world and the origin of the world.
        """
        min_border, max_border = self.get_world_borders()
        if min_border is None or max_border is None:
            return (None, None)
        width = int(round(max_border.x - min_border.x)) + 1
        height = int(round(max_border.y - min_border.y)) + 1
        if self.last_prediction is not None and \
                self.last_prediction.shape == (height, width):
            predicted = self.last_prediction
            reset_saved_prediction = False
        else:
            predicted = np.zeros([height, width])
            reset_saved_prediction = True
        kernel = get_obstacle_filter()
        for (position, observations) in self.map.items():
            if not reset_saved_prediction and observations.used_in_prediction:
                continue
            pos_x = int(round(position.x - min_border.x))
            pos_y = int(round(position.y - min_border.y))
            observations.used_in_prediction = True
            for obs in observations:
                x = int(round(obs.location.x - min_border.x))
                y = int(round(obs.location.y - min_border.y))
                predicted = apply_filter_on_coordinate(predicted, x, y, kernel)
                predicted = apply_function_on_path(predicted, pos_x, pos_y, x,
                                                   y, lambda x: x - 6)
        self.last_prediction = predicted
        predicted = gaussian_filter(predicted, sigma=sigma)
        self.last_prediction_blurred = predicted
        return (predicted, min_border)

    def get_state_on_coordiante(self, location: geometry.Point, blurred=True):
        min_border, _ = self.get_world_borders()
        x = int(round(location.x - min_border.x))
        y = int(round(location.y - min_border.y))
        if blurred:
            return self.last_prediction_blurred[y][x]
        else:
            return self.last_prediction[y][x]

    def is_surrrounding_free(self, location: geometry.Point, radius: int = 5,
                             threshold: float = 0.0):
        loc_x, loc_y = *location,
        for yi in range(-radius, radius + 1):
            for xi in range(-radius, radius + 1):
                point = geometry.Point(loc_x + xi, loc_y + yi)
                if self.point_in_bounds(point) and \
                        self.get_state_on_coordiante(point) > threshold:
                    return False
        return True

    def perc_unknown_surround(self, location: geometry.Point,
                              radius: int = 5) -> float:
        """
        Returns percentage of unknown cells around location. Points that are
        not within the world borders are not included in calculation.
        """
        loc_x, loc_y = *location,
        count = 0
        total = 0
        for yi in range(-radius, radius + 1):
            for xi in range(-radius, radius + 1):
                point = geometry.Point(loc_x + xi, loc_y + yi)
                in_bounds = self.point_in_bounds(point)
                if in_bounds:
                    total += 1
                    if self.get_state_on_coordiante(point) == 0:
                        count += 1
        return count / total

    def get_random_point(self, min_value: float = np.NINF,
                         max_value: float = np.Inf, blurred=True) \
            -> geometry.Point:
        """
        Returns a random point with value between min_value and max_value.
        Returns None if there is no such a value.
        """
        if blurred:
            grid = self.last_prediction_blurred
        else:
            grid = self.last_prediction

        candidates = []
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                if min_value <= grid[y][x] <= max_value:
                    candidates.append((x, y))
        if len(candidates) == 0:
            return None

        min_border, _ = self.get_world_borders()
        index = random.randint(0, len(candidates) - 1)
        x, y = candidates[index]
        return geometry.Point(min_border.x + x, min_border.y + y)

    def print(self):
        s = []
        for y in range(len(self.last_prediction) - 1, -1, -1):
            for x in range(len(self.last_prediction[y])):
                s.append(f"{self.last_prediction[y][x]:3.0f}")
            s.append("\n")
        print(''.join(s))
