import logging
import queue
import random
import socket
import time

import slam.agent.agent as agent
import slam.agent.sensor as sensor
import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.action as action
import slam.planner.planner as planner
import slam.ssocket as ssocket
import slam.world.observed as oworld
import slam.world.simulated as sworld
from slam.common.enums import Message, PathId
from slam.config import config


class Robot(agent.Agent):
    def __init__(self, data_queue: queue.Queue, origin: geometry.Pose = None,
                 robot_size: float = 10.0, scanning_precision: int = 20,
                 view_angle: int = 180, **kwargs):
        super().__init__(data_queue)
        self.pose = origin if origin else geometry.Pose(0, 0, 0)
        self.robot_size = robot_size
        self.scanning_precision = scanning_precision
        self.view_angle = view_angle
        self.observation_queue = queue.Queue()
        self.observed_world = oworld.ObservedWorld()

        self.init_planner()
        self.init_sensor()
        self.scanner.start()

        # Send initial position to the queue
        data = datapoint.Pose(*self.pose, path_id=PathId.ROBOT_HISTORY)
        self.data_queue.put(data)

    def init_sensor(self):
        self.scanner = sensor.DummySensor(self.observation_queue,
                                          self.view_angle,
                                          self.scanning_precision)

    def init_planner(self):
        move_action = action.Action(self.move_forward)
        turn_move_action = action.Action(self.rotate_move_action)
        self.planner = planner.DummyPlanner(move_action=move_action,
                                            turn_move_action=turn_move_action)

    def move_forward(self, distance: float):
        logging.info(f"Move forward for {distance:.2f}.")
        self.pose.move_forward(distance)

    def rotate(self, angle: int):
        logging.info(f"Rotate for {angle:.2f} degrees.")
        self.pose.rotate(angle)

    def rotate_move_action(self, angle: int = 0, distance: float = 0.0):
        self.rotate(angle)
        self.move_forward(distance)

    def scan(self):
        logging.info(f"Scan {self.view_angle/2} in each direction.")
        self.scanner.scan_flag.set()
        while not self.shutdown_flag.is_set() and \
                (measurement := self.observation_queue.get()) is not None:
            polar = measurement.polar
            polar.change(angle=self.pose.orientation.in_degrees())
            location = self.pose.position.plus_polar(polar)
            observed_data = datapoint.Observation(*location, measurement.type)
            self.data_queue.put(observed_data)
            pose_data = datapoint.Pose(*self.pose)
            self.observed_world.add_observation(pose_data, observed_data)

    def perform_action(self):
        self.scan()
        action = self.planner.select_next_action(self.pose)

        while not self.data_queue.empty():
            time.sleep(0.5)
            if self.shutdown_flag.is_set():
                logging.info("Shutdown flag set")
                return False

        if action is None:
            logging.info("Done")
            return False

        time.sleep(1)

        action.execute()

        logging.info(f"\tNew pose: {self.pose}")

        data = datapoint.Pose(*self.pose, path_id=PathId.ROBOT_HISTORY)
        self.data_queue.put(data)

        self.data_queue.put(Message.DELETE_TEMPORARY_DATA)

        return True

    def die(self):
        self.scanner.shutdown_flag.set()
        self.scanner.join()
        logging.info("Dead")


class SimulatedRobot(Robot):
    def __init__(self, data_queue: queue.Queue, robot_size: float = 10.0,
                 scanning_precision: int = 20, view_angle: int = 180,
                 world_number: int = 0, limited_view: float = None):
        self.simulated_world = sworld.PredefinedWorld(world_number)
        self.limited_view = limited_view
        origin = self.simulated_world.pose
        super().__init__(data_queue, origin, robot_size, scanning_precision,
                         view_angle)

    def init_sensor(self):
        args = [
            self.simulated_world,
            self.observation_queue,
        ]
        kwargs = {
            "view_angle": self.view_angle,
            "precision": self.scanning_precision
        }
        if self.limited_view is not None:
            scanner = sensor.LimitedInformationSensor
            kwargs["max_distance"] = self.limited_view
            kwargs["safety_distance"] = self.robot_size / 2
        else:
            scanner = sensor.FullInformationSensor
        self.scanner = scanner(*args, **kwargs)

    def init_planner(self):
        turn_action = action.Action(self.rotate)
        move_action = action.Action(self.move_forward)
        turn_move_action = action.Action(self.rotate_move_action)
        self.planner = planner.RrtPlanner(self.observed_world, self.data_queue,
                                          turn_action=turn_action,
                                          move_action=move_action,
                                          turn_move_action=turn_move_action,
                                          shutdown_flag=self.shutdown_flag,
                                          robot_size=self.robot_size)

    def scan(self):
        self.simulated_world.update_pose(self.pose)
        super().scan()


class LegoRobot(Robot):
    def __init__(self, *args, **kwargs):
        self.init_socket()
        super().__init__(*args, **kwargs)

    def init_sensor(self):
        self.scanner = sensor.LegoIrSensor(self.observation_queue, self.socket,
                                           self.view_angle,
                                           self.scanning_precision,
                                           self.robot_size / 2)

    def init_planner(self):
        turn_action = action.Action(self.rotate)
        move_action = action.Action(self.move_forward)
        turn_move_action = action.Action(self.rotate_move_action)
        self.planner = planner.RrtPlanner(self.observed_world, self.data_queue,
                                          turn_action=turn_action,
                                          move_action=move_action,
                                          turn_move_action=turn_move_action,
                                          shutdown_flag=self.shutdown_flag,
                                          robot_size=self.robot_size)

    def init_socket(self):
        self.socket = ssocket.Socket(config.HOST, config.PORT)

    def move_forward(self, distance: float):
        super().move_forward(distance)

        @ssocket.handle_socket_error(cleanup=lambda: self.shutdown_flag.set())
        def t_move_forward():
            self.socket.send(f"MOVE {distance:.2f}")
        t_move_forward()

    def rotate(self, angle: int):
        super().rotate(angle)

        @ssocket.handle_socket_error(cleanup=lambda: self.shutdown_flag.set())
        def t_rotate():
            self.socket.send(f"ROTATE {angle:.2f}")
        t_rotate()

    def die(self):
        self.socket.close()
        super().die()
