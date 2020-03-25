import logging
import queue
import random
import time

import slam.agent.agent as agent
import slam.common.datapoint as datapoint
import slam.common.geometry as geometry


class Robot(agent.Agent):
    def __init__(self, data_queue: queue.Queue, origin: geometry.Pose = None,
                 scanning_precision: int = 20):
        super().__init__(data_queue)
        self.map = dict()
        self.pose = origin if origin else geometry.Pose(0, 0, 0)
        self.scanning_precision = scanning_precision

        # Send initial position to the queue
        data = datapoint.Position(*self.pose.get_position())
        self.data_queue.put(data)

    def move_forward(self, distance: float):
        logging.info(f"Move forward for {distance}.")
        self.pose.move_forward(distance)

    def rotate(self, angle: int):
        logging.info(f"Rotate for {angle} degrees.")
        self.pose.rotate(angle)

    def scan(self, view_angle: int = 360):
        logging.info(f"Scan {view_angle/2} in each direction.")
        prev_measurement = 10
        robot_position = self.pose.get_position()
        start_angle = self.pose.orientation.in_degrees() - int(view_angle/2)
        for angle in range(start_angle, start_angle + view_angle,
                           self.scanning_precision):
            new_measurement = prev_measurement + random.random() * 2 - 1
            polar = geometry.Polar(angle, new_measurement)
            location = robot_position.plus_polar(polar)

            data = datapoint.Observation(*location)
            self.data_queue.put(data)
            prev_measurement = new_measurement

    def perform_action(self):
        r = random.random()
        if r < 0.3:
            self.scan(180)
        elif r < 0.8:
            distance = random.randint(1, 5)
            self.move_forward(distance)
        else:
            angle = random.randint(1, 360)
            self.rotate(angle)

        logging.info(f"\tNew pose: {self.pose}")

        data = datapoint.Position(*self.pose.get_position())
        self.data_queue.put(data)

        time.sleep(1)
