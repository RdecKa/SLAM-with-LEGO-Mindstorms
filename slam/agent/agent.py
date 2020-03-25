import logging
import queue
import random
import threading
import time

import slam.common.datapoint as datapoint


class Agent(threading.Thread):
    def __init__(self, data_queue: queue.Queue):
        threading.Thread.__init__(self)
        self.data_queue = data_queue
        self.shutdown_flag = threading.Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            logging.info("Alive")
            self.perform_action()
        logging.info("Dead")

    def perform_action(self):
        """
        Dummy action
        """
        time.sleep(1)
        if random.random() < 0.9:
            x = random.randint(0, 10)
            y = random.randint(0, 10)
            if random.random() < 0.5:
                data = datapoint.Observation(x, y)
            else:
                data = datapoint.Position(x, y)
            self.data_queue.put(data)
