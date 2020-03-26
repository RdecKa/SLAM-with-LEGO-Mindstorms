import logging
import queue
import random
import threading
import time

import slam.common.geometry as geometry


class Sensor(threading.Thread):
    def __init__(self, data_queue: queue.Queue, view_angle: int = 360,
                 precision: int = 20):
        threading.Thread.__init__(self)
        self.data_queue = data_queue
        self.shutdown_flag = threading.Event()
        self.scan_flag = threading.Event()
        self.view_angle = view_angle
        self.precision = precision

    def run(self):
        logging.info("Turned sensor on")
        while not self.shutdown_flag.is_set():
            self.scan_flag.wait(3)
            if self.scan_flag.is_set():
                self.scan()
                self.scan_flag.clear()
        logging.info("Turned sensor off")


class DummySensor(Sensor):
    """
    Scanner for dummy scanning. Put scanned values to a queue (as polar
    coordinates). Put None to the queue when scanning is over.
    """
    def __init__(self, data_queue: queue.Queue, view_angle: int = 360,
                 precision: int = 20):
        super().__init__(data_queue, view_angle, precision)

    def scan(self):
        logging.info("Started scanning")
        prev_measurement = 10
        start_angle = int(- self.view_angle / 2)
        for angle in range(start_angle, start_angle + self.view_angle,
                           self.precision):
            new_measurement = prev_measurement + random.random() * 2 - 1
            polar = geometry.Polar(angle, new_measurement)

            self.data_queue.put(polar)
            prev_measurement = new_measurement
            time.sleep(0.5)
        self.data_queue.put(None)
        logging.info("Scanning finished")
