import random
from typing import Callable, Dict, List, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.world.world as world
from slam.common.enums import ObservationType


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
        for key, entry in self.map.items():
            x_coords = [o.location.x for o in entry] + [key.x]
            x_min = min(x_min, min(x_coords))
            x_max = max(x_max, max(x_coords))

            y_coords = [o.location.y for o in entry] + [key.y]
            y_min = min(y_min, min(y_coords))
            y_max = max(y_max, max(y_coords))
        return (geometry.Point(x_min, y_min), geometry.Point(x_max, y_max))

    def get_area_around_point(self, location: geometry.Point, radius: int,
                              blurred: bool = True) -> np.array:
        """
        Returns a square area with the center in location and the square side
        of 2 * radius + 1.
        """
        min_border, max_border = self.get_world_borders()
        loc_x, loc_y = *location,
        x_min = int(round(max(min_border.x, loc_x - radius) - min_border.x))
        x_max = int(round(min(max_border.x, loc_x + radius) - min_border.x))
        y_min = int(round(max(min_border.y, loc_y - radius) - min_border.y))
        y_max = int(round(min(max_border.y, loc_y + radius) - min_border.y))

        if blurred:
            grid = self.last_prediction_blurred
        else:
            grid = self.last_prediction
        area = grid[y_min:y_max+1, x_min:x_max+1]
        return area

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
        kernel = get_obstacle_filter(sigma=1)
        for (position, observations) in self.map.items():
            if not reset_saved_prediction and observations.used_in_prediction:
                continue
            pos_x = int(round(position.x - min_border.x))
            pos_y = int(round(position.y - min_border.y))
            observations.used_in_prediction = True
            for obs in observations:
                x = int(round(obs.location.x - min_border.x))
                y = int(round(obs.location.y - min_border.y))
                if obs.type == ObservationType.OBSTACLE:
                    predicted = apply_filter_on_coordinate(predicted, x, y,
                                                           kernel)
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
        area = self.get_area_around_point(location, radius)
        area_over_threshold = area > threshold
        return not np.any(area_over_threshold)

    def is_path_free(self, start: geometry.Point, end: geometry.Point,
                     radius: int = 5, threshold: float = 0.0):
        pose = geometry.Pose(*start, 0)
        pose.turn_towards(end)
        while pose.position.distance_to(end) > radius:
            pose.move_forward(1.5 * radius)
            if not self.is_surrrounding_free(pose.position, radius=radius,
                                             threshold=threshold):
                return False
        return True

    def perc_unknown_surround(self, location: geometry.Point,
                              radius: int = 5) -> float:
        """
        Returns percentage of unknown cells around location. Points that are
        not within the world borders are not included in calculation.
        """
        total_area_size = ((2 * radius + 1) ** 2)
        area = self.get_area_around_point(location, radius, blurred=True)
        unknown = abs(area) < 1
        unknown_count = np.sum(unknown)
        unknkown_out_of_map = total_area_size - area.size
        unknown_count += unknkown_out_of_map
        return unknown_count / total_area_size

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

        candidates = np.argwhere(
            np.logical_and(grid >= min_value, grid <= max_value))

        if len(candidates) == 0:
            return None

        min_border, max_border = self.get_world_borders()
        index = random.randint(0, len(candidates) - 1)
        y, x = candidates[index]
        new_x = min(min_border.x + x, max_border.x)
        new_y = min(min_border.y + y, max_border.y)
        return geometry.Point(new_x, new_y)

    def print(self):
        s = []
        for y in range(len(self.last_prediction) - 1, -1, -1):
            for x in range(len(self.last_prediction[y])):
                s.append(f"{self.last_prediction[y][x]:3.0f}")
            s.append("\n")
        print(''.join(s))
