import logging
import queue
import random
import threading
from typing import Tuple

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.graph as sgraph
import slam.world.observed as oworld
from slam.common.enums import Existence, PathId


class PathPlanner():
    def __init__(self, observed_world: oworld.ObservedWorld,
                 shutdown_flag: threading.Event,
                 max_step_size: int = 10, min_step_size: int = 0,
                 tilt_towards_goal: float = 0.5,
                 distance_tollerance: float = 5.0,
                 data_queue: queue.Queue = None, robot_size: float = 10.0):
        self.observed_world = observed_world
        self.max_step_size = max_step_size
        self.min_step_size = min_step_size
        self.tilt_towards_goal = tilt_towards_goal
        self.tollerance = distance_tollerance
        self.data_queue = data_queue
        self.robot_size = robot_size
        self.shutdown_flag = shutdown_flag

    def plan_next_step(self, start: geometry.Point, goal: geometry.Point) \
            -> geometry.Point:
        graph = sgraph.Graph()
        graph.add_node(sgraph.Node(start))

        node = self.find_path(graph, goal)
        if node is None:
            return None

        def add_point_to_path(location: geometry.Point, color: Tuple):
            data = datapoint.DataPoint(*location, color=color,
                                       path_id=PathId.ROBOT_PATH_PLAN,
                                       path_style="--",
                                       existence=Existence.TEMPORARY)
            self.data_queue.put(data)

        # Add goal to path
        add_point_to_path(goal, (1., 0.6, 0., 1.))

        if node.parent is None:
            logging.warning(f"Path planner returned starting point")
            return node.location

        color = (1., 0.6, 0., 0.3)
        while node.parent is not None:
            old_node = node
            add_point_to_path(node.location, color)
            node = node.parent

        add_point_to_path(start, color)

        return old_node.location

    def find_path(self, graph: sgraph.Graph, goal: geometry.Point):
        """
        Returns a node that is less than self.tollerance away from the
        goal. Use Node.parent recursively to get the whole path.
        """
        min_step_size = self.min_step_size
        while not self.shutdown_flag.is_set():
            r = random.random()
            if r < self.tilt_towards_goal:
                approx_target = goal

                # Randomly change the target
                d = abs(random.gauss(0, self.tollerance))
                a = random.randint(0, 359)
                p = geometry.Polar(a, d)
                target = approx_target.plus_polar(p)
            else:
                # Select random point
                target = self.observed_world.get_random_point()

            # Find node that is closest to the target
            parent = min(graph, key=get_fun_distance_to(target))

            angle = parent.location.angle_to(target).in_degrees()
            distance = parent.location.distance_to(target)
            if distance < min_step_size:
                # Do not plan too small steps
                min_step_size *= 0.99
                if min_step_size < self.min_step_size / 4:
                    logging.warning(f"min_step_size reduced to a quarter "
                                    f"({min_step_size:.2f})")
                continue
            step = min(self.max_step_size, distance)
            polar = geometry.Polar(angle, step)

            candidate = parent.location.plus_polar(polar)
            if not self.observed_world.point_in_bounds(candidate):
                continue

            free_radius = int(self.robot_size / 2)
            if not self.observed_world.is_surrrounding_free(candidate,
                                                            free_radius,
                                                            threshold=1):
                # Candidate is not free
                continue

            if not self.observed_world.is_path_free(parent.location, candidate,
                                                    radius=free_radius,
                                                    threshold=1.0):
                # Path to the candidate is not free
                continue

            new_node = sgraph.Node(candidate, parent)
            graph.add_node(new_node)
            min_step_size = self.min_step_size

            if candidate.distance_to(goal) < self.tollerance:
                return new_node

            if len(graph) > 200:
                # Give up trying to find path to the goal
                logging.warning(f"Couldn't find a path to node {goal}")
                return None
        return None


def get_fun_distance_to(goal: geometry.Point):
    def f(node: sgraph.Node):
        return node.location.distance_to(goal)
    return f
