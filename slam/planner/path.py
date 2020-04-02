import logging
import queue
import random

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.graph as sgraph
import slam.world.observed as oworld
from slam.common.enums import Existence, PathId


class PathPlanner():
    def __init__(self, observed_world: oworld.ObservedWorld,
                 step_size: int = 10, tilt_towards_goal: float = 0.7,
                 distance_tollerance: float = 5.0,
                 data_queue: queue.Queue = None):
        self.observed_world = observed_world
        self.step_size = step_size
        self.tilt_towards_goal = tilt_towards_goal
        self.tollerance = distance_tollerance
        self.data_queue = data_queue

    def plan_next_step(self, start: geometry.Point, goal: geometry.Point):
        graph = sgraph.Graph()
        graph.add_node(sgraph.Node(start))

        node = self.find_path(graph, goal)
        if node is None:
            return None

        # Add goal to path
        data = datapoint.DataPoint(*goal, color=(1., 0.6, 0., 1.),
                                   path_id=PathId.ROBOT_PATH_PLAN,
                                   path_style="--",
                                   existence=Existence.TEMPORARY)
        self.data_queue.put(data)

        if node.parent is None:
            logging.warning(f"Path planner returned starting point")
            return node.location

        color = (1., 0.6, 0., 0.3)
        while node.parent is not None:
            old_node = node

            data = datapoint.DataPoint(*node.location, color=color,
                                       path_id=PathId.ROBOT_PATH_PLAN,
                                       path_style="--",
                                       existence=Existence.TEMPORARY)
            self.data_queue.put(data)
            node = node.parent

        # Add starting position to path
        data = datapoint.DataPoint(*start, color=(1., 0.6, 0., 0.3),
                                   path_id=PathId.ROBOT_PATH_PLAN,
                                   path_style="--",
                                   existence=Existence.TEMPORARY)
        self.data_queue.put(data)

        return old_node.location

    def find_path(self, graph: sgraph.Graph, goal: geometry.Point):
        """
        Returns a node that is less than self.tollerance away from the
        goal. Use Node.parent recursively to get the whole path.
        """
        threshold = -100
        while True:
            threshold *= 0.9
            r = random.random()
            if r < self.tilt_towards_goal:
                target = goal
            else:
                # Select random point
                while True:
                    target = self.observed_world.get_random_point(
                        max_value=threshold)
                    if target is not None:
                        break
                    threshold /= 2

            # Find node that is closest to the target
            parent = min(graph, key=get_fun_distance_to(target))

            angle = parent.location.angle_to(target).in_degrees()
            distance = parent.location.distance_to(target)
            step = min(self.step_size, distance)
            polar = geometry.Polar(angle, step)

            candidate = parent.location.plus_polar(polar)
            if not self.observed_world.point_in_bounds(candidate):
                logging.warning(f"Path candidate out of bounds {candidate}")
                continue

            if self.observed_world.is_surrrounding_free(candidate, 3):
                # Free spot
                new_node = sgraph.Node(candidate, parent)
                graph.add_node(new_node)

                if candidate.distance_to(goal) < self.tollerance:
                    return new_node

                if len(graph) > 200:
                    # Give up trying to find path to the goal
                    logging.warning(f"Couldn't find a path to node {goal}")
                    return None


def get_fun_distance_to(goal: geometry.Point):
    def f(node: sgraph.Node):
        return node.location.distance_to(goal)
    return f
