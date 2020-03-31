import queue

import numpy as np
from scipy.signal import convolve2d

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.action as action
import slam.planner.path as spath
import slam.world.observed as oworld
from slam.common.enums import Message


class Planner():
    def __init__(self, observed_world: oworld.ObservedWorld,
                 data_queue: queue.Queue, turn_action: action.Action,
                 move_action: action.Action, turn_move_action: action.Action,
                 distance_tollerance: float = 5.0,
                 angle_tollerance: float = 5.0):
        self.observed_world = observed_world
        self.data_queue = data_queue
        self.distance_tollerance = distance_tollerance
        self.angle_tollerance = angle_tollerance
        self.turn_action = turn_action
        self.move_action = move_action
        self.turn_move_action = turn_move_action
        self.path_planner = spath.PathPlanner(observed_world,
                                              data_queue=data_queue)

    def select_next_action(self, current_pose: geometry.Pose) -> \
            action.ActionWithParams:

        goal = self.select_new_goal(current_pose)

        if goal is None:
            return None

        intermediate_goal = self.path_planner.plan_next_step(
            current_pose.position, goal)

        angle_deg = current_pose.angle_to_point(intermediate_goal).in_degrees()
        distance = current_pose.position.distance_to(intermediate_goal)

        if abs(angle_deg) > self.angle_tollerance:
            return action.ActionWithParams(self.turn_move_action, angle_deg,
                                           distance)

        return action.ActionWithParams(self.move_action, distance)

    def select_new_goal(self, current_pose: geometry.Pose):
        predicted_world, origin = self.observed_world.predict_world()
        if predicted_world is None or origin is None:
            return
        self.data_queue.put(datapoint.Prediction(*origin, predicted_world))
        self.data_queue.put(Message.DELETE_TEMPORARY_DATA)
        frontier = self.get_unknown_locations(self.observed_world)
        self.data_queue.put(frontier)

        return self.select_from_frontier(frontier, current_pose)

    def get_unknown_locations(self, observed_world: oworld.ObservedWorld,
                              kernel_size: int = 5,
                              sigma: int = 1) -> datapoint.Frontier:
        """
        Finds locations where the search can be continued (locations free of
        obstacles that are near to locations with unknown occupancy).
        """
        grid = observed_world.last_prediction_blurred
        kernel = np.ones([kernel_size, kernel_size])
        conv = convolve2d(grid, kernel, mode="same", boundary="symm")
        y_shape, x_shape = grid.shape
        frontier = []
        min_border, _ = observed_world.get_world_borders()
        for yi in range(y_shape):
            for xi in range(x_shape):
                if -0.1 < grid[yi][xi] < 0 and conv[yi][xi] < 0:
                    x = min_border.x + xi
                    y = min_border.y + yi
                    frontier.append(geometry.Point(x, y))
        return datapoint.Frontier(min_border.x, min_border.y, frontier)

    def select_from_frontier(self, frontier: datapoint.Frontier,
                             current_pose: geometry.Pose) -> geometry.Point:
        if len(frontier) == 0:
            return None

        num_points = len(frontier)
        distances = np.zeros([num_points, num_points])
        for i in range(num_points):
            for j in range(i+1, num_points):
                d = frontier[i].location.distance_to(frontier[j].location)
                distances[i][j] = d
                distances[j][i] = d

        # Choose between points that have some neighbouring points
        count = [sum(1 for d in distances[i] if d < self.distance_tollerance)
                 for i in range(num_points)]
        candidates = [p for (i, p) in enumerate(frontier) if count[i] >= 3]

        if len(candidates) == 0:
            return None

        nearest = min(candidates,
                      key=lambda p: geometry.Point(*p.location).distance_to(
                        current_pose.position))
        return geometry.Point(*nearest.location)
