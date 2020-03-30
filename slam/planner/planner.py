import queue

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.action as action
import slam.world.observed as oworld
from slam.common.enums import Message


class Planner():
    def __init__(self, observed_world: oworld.ObservedWorld,
                 data_queue: queue.Queue, turn_action: action.Action,
                 move_action: action.Action, distance_tollerance: float = 5.0,
                 angle_tollerance: float = 5.0):
        self.observed_world = observed_world
        self.data_queue = data_queue
        self.current_goal: geometry.Point = None
        self.distance_tollerance = distance_tollerance
        self.angle_tollerance = angle_tollerance
        self.turn_action = turn_action
        self.move_action = move_action
        self.max_movement_forward = 10

    def select_next_action(self, current_pose: geometry.Pose) -> \
            action.ActionWithParams:
        current_position = current_pose.position
        if (goal := self.current_goal) is None or \
                current_position.distance_to(goal) < self.distance_tollerance:
            self.select_new_goal(current_pose)

        if self.current_goal is None:
            return None

        angle_deg = current_pose.angle_to_point(self.current_goal).in_degrees()
        if abs(angle_deg) > self.angle_tollerance:
            return action.ActionWithParams(self.turn_action, angle_deg)

        distance = current_pose.position.distance_to(self.current_goal)
        move_for = min(self.max_movement_forward, distance)
        return action.ActionWithParams(self.move_action, move_for)

    def select_new_goal(self, current_pose: geometry.Pose):
        predicted_world, origin = self.observed_world.predict_world()
        if predicted_world is None or origin is None:
            return
        self.data_queue.put(datapoint.Prediction(*origin, predicted_world))
        self.data_queue.put(Message.DELETE_TEMPORARY_DATA)
        frontier = self.observed_world.get_unknown_locations()
        self.data_queue.put(frontier)

        next_location = self.select_from_frontier(frontier, current_pose)
        self.current_goal = next_location

    def select_from_frontier(self, frontier: datapoint.Frontier,
                             current_pose: geometry.Pose) -> geometry.Point:
        if len(frontier) == 0:
            return None

        nearest = min(frontier,
                      key=lambda p: geometry.Point(*p.location).distance_to(
                        current_pose.position))
        return geometry.Point(*nearest.location)
