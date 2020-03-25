import logging
import queue
import random
import threading
import time


class Agent(threading.Thread):
    def __init__(self, data_queue: queue.Queue):
        threading.Thread.__init__(self)
        self.data_queue = data_queue
        self.shutdown_flag = threading.Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            logging.info("Alive")
            time.sleep(1)
            if random.random() < 0.4:
                logging.info("Lucky!")
                x = random.randint(0, 10)
                y = random.randint(0, 10)
                self.data_queue.put((x, y))
        logging.info("Dead")
