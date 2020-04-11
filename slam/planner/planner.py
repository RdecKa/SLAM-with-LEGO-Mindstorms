import logging
import queue
import random
import threading

import numpy as np

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.action as action
import slam.planner.path as spath
import slam.world.observed as oworld


class Planner():
    def __init__(self, turn_action: action.Action, move_action: action.Action,
                 turn_move_action: action.Action):
        logging.info(f"Using planner: {type(self).__name__}")
        self.turn_action = turn_action
        self.move_action = move_action
        self.turn_move_action = turn_move_action

    def select_next_action(self, current_pose: geometry.Pose):
        raise NotImplementedError


class RrtPlanner(Planner):
    def __init__(self, observed_world: oworld.ObservedWorld,
                 data_queue: queue.Queue, turn_action: action.Action,
                 move_action: action.Action, turn_move_action: action.Action,
                 shutdown_flag: threading.Event,
                 distance_tollerance: float = None,
                 angle_tollerance: float = 3.0, robot_size: float = 10.0):
        super().__init__(turn_action, move_action, turn_move_action)
        self.observed_world = observed_world
        self.data_queue = data_queue
        self.angle_tollerance = angle_tollerance
        self.robot_size = robot_size
        self.shutdown_flag = shutdown_flag

        if distance_tollerance is not None:
            self.distance_tollerance = distance_tollerance
        else:
            self.distance_tollerance = robot_size / 2

        self.path_planner = spath.PathPlanner(observed_world,
                                              shutdown_flag=shutdown_flag,
                                              max_step_size=2*robot_size,
                                              min_step_size=robot_size/3,
                                              distance_tollerance=self.distance_tollerance,
                                              data_queue=data_queue,
                                              robot_size=robot_size)

    def select_next_action(self, current_pose: geometry.Pose) -> \
            action.ActionWithParams:
        goal = self.select_new_goal(current_pose)
        if goal is None:
            return None

        angle_deg = current_pose.angle_to_point(goal).in_degrees()
        distance = current_pose.position.distance_to(goal)

        if abs(angle_deg) > self.angle_tollerance:
            return action.ActionWithParams(self.turn_move_action, angle_deg,
                                           distance)

        return action.ActionWithParams(self.move_action, distance)

    def select_new_goal(self, current_pose: geometry.Pose):
        predicted_world, origin = self.observed_world.predict_world()
        if predicted_world is None or origin is None:
            return None

        self.data_queue.put(datapoint.Prediction(*origin, predicted_world))
        frontier = self.get_unknown_locations()
        self.data_queue.put(frontier)

        intermediate_goal = None
        c = 0
        num_allowed_tries = 5
        while intermediate_goal is None and c < num_allowed_tries and \
                not self.shutdown_flag.is_set():
            select_randomly = c > 0
            goal = self.select_from_frontier(frontier, current_pose,
                                             select_randomly)
            if goal is None:
                # No candidates remain
                return None

            if self.observed_world.is_path_free(current_pose.position, goal,
                                                radius=int(self.robot_size/2),
                                                threshold=1):
                return goal

            intermediate_goal = self.path_planner.plan_next_step(
                current_pose.position, goal)
            c += 1

        if intermediate_goal is None:
            if self.shutdown_flag.is_set():
                logging.info("Planning interrupted.")
            else:
                try_text = f"{'try' if num_allowed_tries == 1 else 'tries'}"
                logging.warning(f"Couldn't find a reachable goal in "
                                f"{num_allowed_tries} {try_text}")
            return None

        return intermediate_goal

    def get_unknown_locations(self) \
            -> datapoint.Frontier:
        """
        Finds locations where the search can be continued (locations free of
        obstacles that are near to locations with unknown occupancy).
        TODO: Make selection more precize.
        """
        grid = self.observed_world.last_prediction_blurred
        y_shape, x_shape = grid.shape
        frontier = []
        min_border, _ = self.observed_world.get_world_borders()
        for yi in range(y_shape):
            for xi in range(x_shape):
                x = min_border.x + xi
                y = min_border.y + yi
                p = geometry.Point(x, y)
                if grid[yi][xi] >= 0:
                    continue
                if grid[yi][xi] < -10:
                    continue  # Enough evidence that here is a free spot
                if not self.observed_world.is_surrrounding_free(
                        p, radius=int(self.robot_size / 2), threshold=1.0):
                    continue
                u = self.observed_world.perc_unknown_surround(
                    p, radius=int(self.robot_size / 2))
                if u < 0.3:
                    continue
                frontier.append(p)
        return datapoint.Frontier(min_border.x, min_border.y, frontier)

    def select_from_frontier(self, frontier: datapoint.Frontier,
                             current_pose: geometry.Pose,
                             select_randomly: bool = False) -> geometry.Point:
        """
        Selects a point to be visited next.
        TODO: Take orientation in consideration.
        """
        if len(frontier) == 0:
            return None

        num_points = len(frontier)
        distances = np.zeros([num_points, num_points])
        for i in range(num_points):
            p = frontier[i].location
            for j in range(i+1, num_points):
                d = p.distance_to(frontier[j].location)
                distances[i][j] = d
                distances[j][i] = d

        # Choose between points that have some neighbouring points
        count = [sum(1 for d in distances[i] if d < self.distance_tollerance)
                 for i in range(num_points)]
        candidates = [p for (i, p) in enumerate(frontier) if count[i] >= 3]

        if len(candidates) == 0:
            return None

        if select_randomly:
            index = random.randint(0, len(candidates) - 1)
            chosen = candidates[index]
            logging.info(f"Selected goal: {chosen.location} "
                         f"(selected randomly)")
        else:
            chosen = min(candidates,
                         key=lambda p: geometry.Point(*p.location).distance_to(
                            current_pose.position))
            logging.info(f"Selected goal: {chosen.location}")
        return geometry.Point(*chosen.location)


class DummyPlanner(Planner):
    def __init__(self, move_action: action.Action,
                 turn_move_action: action.Action):
        super().__init__(None, move_action, turn_move_action)

    def select_next_action(self, current_pose: geometry.Pose) -> \
            action.ActionWithParams:
        distance = random.randint(1, 10)
        if random.random() < 0.7:
            return action.ActionWithParams(self.move_action, distance)
        angle = random.randint(1, 359)
        return action.ActionWithParams(self.turn_move_action, angle, distance)
