import logging
import queue
import random
import time

import slam.agent.agent as agent
import slam.agent.sensor as sensor
import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.planner.action as action
import slam.planner.planner as planner
import slam.world.observed as oworld
import slam.world.simulated as sworld


class Robot(agent.Agent):
    def __init__(self, data_queue: queue.Queue, origin: geometry.Pose = None,
                 scanning_precision: int = 20, view_angle: int = 180):
        super().__init__(data_queue)
        self.pose = origin if origin else geometry.Pose(0, 0, 0)
        self.scanning_precision = scanning_precision
        self.view_angle = view_angle
        self.observation_queue = queue.Queue()
        self.observed_world = oworld.ObservedWorld()
        turn_action = action.Action(self.rotate)
        move_action = action.Action(self.move_forward)
        self.planner = planner.Planner(self.observed_world, data_queue,
                                       turn_action=turn_action,
                                       move_action=move_action)

        self.init_sensor()
        self.scanner.start()

        # Send initial position to the queue
        data = datapoint.Pose(*self.pose)
        self.data_queue.put(data)

    def init_sensor(self):
        self.scanner = sensor.DummySensor(self.observation_queue,
                                          self.view_angle,
                                          self.scanning_precision)

    def move_forward(self, distance: float):
        logging.info(f"Move forward for {distance}.")
        self.pose.move_forward(distance)

    def rotate(self, angle: int):
        logging.info(f"Rotate for {angle} degrees.")
        self.pose.rotate(angle)

    def scan(self):
        logging.info(f"Scan {self.view_angle/2} in each direction.")
        self.scanner.scan_flag.set()
        while (observed := self.observation_queue.get()) is not None:
            observed.change(self.pose.orientation.in_degrees())
            location = self.pose.position.plus_polar(observed)
            observed_data = datapoint.Observation(*location)
            self.data_queue.put(observed_data)
            pose_data = datapoint.Pose(*self.pose)
            self.observed_world.add_observation(pose_data, observed_data)

    def perform_action(self):
        r = random.random()
        if r < 0.3:
            self.scan()
        elif r < 0.8:
            distance = random.randint(1, 3)
            self.move_forward(distance)
        else:
            angle = random.randint(1, 30) - 15
            self.rotate(angle)

        logging.info(f"\tNew pose: {self.pose}")

        data = datapoint.Pose(*self.pose)
        self.data_queue.put(data)

        time.sleep(.5)
        return True

    def die(self):
        self.scanner.shutdown_flag.set()
        self.scanner.join()
        logging.info("Dead")


class SimulatedRobot(Robot):
    def __init__(self, data_queue: queue.Queue, origin: geometry.Pose = None,
                 scanning_precision: int = 20, view_angle: int = 180):
        self.simulated_world = sworld.SimulatedWorld()
        super().__init__(data_queue, origin, scanning_precision, view_angle)
        self.simulated_world.update_pose(self.pose)

    def init_sensor(self):
        self.scanner = sensor.FullInformationSensor(self.simulated_world,
                                                    self.observation_queue,
                                                    self.view_angle,
                                                    self.scanning_precision)

    def scan(self):
        self.simulated_world.update_pose(self.pose)
        super().scan()

    def perform_action(self):
        self.scan()
        action = self.planner.select_next_action(self.pose)
        if action is None:
            logging.info("Done")
            return False

        action.execute()

        logging.info(f"\tNew pose: {self.pose}")

        data = datapoint.Pose(*self.pose)
        self.data_queue.put(data)

        time.sleep(.5)
        return True
