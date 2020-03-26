import logging
import queue
import random
import time

import slam.agent.agent as agent
import slam.agent.sensor as sensor
import slam.common.datapoint as datapoint
import slam.common.geometry as geometry


class Robot(agent.Agent):
    def __init__(self, data_queue: queue.Queue, origin: geometry.Pose = None,
                 scanning_precision: int = 20):
        super().__init__(data_queue)
        self.pose = origin if origin else geometry.Pose(0, 0, 0)
        self.scanning_precision = scanning_precision
        self.observation_queue = queue.Queue()
        self.scanner = sensor.DummySensor(self.observation_queue, 180)
        self.scanner.start()

        # Send initial position to the queue
        data = datapoint.Position(*self.pose.position)
        self.data_queue.put(data)

    def move_forward(self, distance: float):
        logging.info(f"Move forward for {distance}.")
        self.pose.move_forward(distance)

    def rotate(self, angle: int):
        logging.info(f"Rotate for {angle} degrees.")
        self.pose.rotate(angle)

    def scan(self, view_angle: int = 360):
        logging.info(f"Scan {view_angle/2} in each direction.")
        self.scanner.scan_flag.set()
        while (observed := self.observation_queue.get()) is not None:
            observed.change(self.pose.orientation.in_degrees())
            location = self.pose.position.plus_polar(observed)
            data = datapoint.Observation(*location)
            self.data_queue.put(data)

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

        data = datapoint.Position(*self.pose.position)
        self.data_queue.put(data)

        time.sleep(1)

    def die(self):
        self.scanner.shutdown_flag.set()
        self.scanner.join()
        logging.info("Dead")
