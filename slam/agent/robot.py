import logging
import queue
import random
import time

import slam.agent.agent as agent
import slam.common.datapoint as datapoint
import slam.common.geometry as geometry


class Robot(agent.Agent):
    def __init__(self, data_queue: queue.Queue):
        super().__init__(data_queue)
        self.map = dict()
        self.pose = geometry.Pose(0, 0, 0)

    def move_forward(self, distance: float):
        logging.info(f"Move formward for {distance}.")
        self.pose.move_forward(distance)

    def rotate(self, angle: int):
        logging.info(f"Rotate for {angle} degrees.")
        self.pose.rotate(angle)

    def scan(self, view_angle: int):
        logging.info(f"Scan {view_angle/2} in each direction.")

    def perform_action(self):
        r = random.random()
        if r < 0.7:
            distance = random.randint(1, 5)
            self.move_forward(distance)
        else:
            angle = random.randint(1, 360)
            self.rotate(angle)

        data = datapoint.Position(*self.pose.get_coordinates())
        self.data_queue.put(data)

        time.sleep(1)
