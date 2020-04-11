import logging
import queue
import random
import socket
import threading
import time

import slam.common.geometry as geometry
import slam.ssocket as ssocket
import slam.world.simulated as sworld
from slam.common.enums import ObservationType


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
        logging.info(f"Turned sensor {type(self).__name__} on")
        while not self.shutdown_flag.is_set():
            self.scan_flag.wait(1)
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
        logging.info("Scanning started")
        prev_measurement = 10
        start_angle = int(- self.view_angle / 2)
        for angle in range(start_angle, start_angle + self.view_angle + 1,
                           self.precision):
            new_measurement = prev_measurement + random.random() * 2 - 1
            polar = geometry.Polar(angle, new_measurement)
            data = SensorMeasurement(polar, ObservationType.OBSTACLE)

            self.data_queue.put(data)
            prev_measurement = new_measurement
            time.sleep(0.5)
        self.data_queue.put(None)
        logging.info("Scanning finished")


class SimulatedSensor(Sensor):
    """
    Sensor that has some information about the real (simulated) world.
    """
    def __init__(self, simulated_world: sworld.SimulatedWorld,
                 data_queue: queue.Queue, view_angle: int = 360,
                 precision: int = 20):
        super().__init__(data_queue, view_angle, precision)
        self.world = simulated_world

    def scan(self):
        logging.info("Scanning started")
        start_angle = int(- self.view_angle / 2)
        for angle in range(start_angle, start_angle + self.view_angle + 1,
                           self.precision):
            data = self.measure(angle)
            self.data_queue.put(data)
            time.sleep(0.2)
        self.data_queue.put(None)
        logging.info("Scanning finished")

    def measure(self, angle):
        raise NotImplementedError


class FullInformationSensor(SimulatedSensor):
    """
    Sensor that has full information about the world.
    """
    def measure(self, angle):
        measurement = self.world.get_distance_to_wall(angle)
        polar = geometry.Polar(angle, measurement)
        data = SensorMeasurement(polar, ObservationType.OBSTACLE)
        return data


class LimitedInformationSensor(SimulatedSensor):
    """
    Sensor that has a limited view.
    """
    def __init__(self, *args, max_distance: float = 30.0,
                 safety_distance: float = 15.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_distance = max_distance
        self.safety_distance = safety_distance

    def measure(self, angle):
        measurement = self.world.get_distance_to_wall(angle)
        if measurement > self.max_distance:
            measurement = self.max_distance - self.safety_distance
            otype = ObservationType.FREE
        else:
            otype = ObservationType.OBSTACLE

        polar = geometry.Polar(angle, measurement)
        data = SensorMeasurement(polar, otype)
        return data


class LegoIrSensor(Sensor):
    """
    LEGO infrared sensor.
    Initially turn robot for view_angle // 2. Then change direction of scanning
    for each run.
    Example: view_angle=180, precision=90
        Init: rotate for 90
        Odd run (1, 3 ...):  scan 90, 0, -90
        Even run (2, 4 ...): scan -90, 0, 90
    """
    def __init__(self, data_queue: queue.Queue, socket: socket.socket,
                 view_angle: int = 360, precision: int = 20,
                 safety_distance: float = 10.0):
        super().__init__(data_queue, view_angle, precision)
        self.socket = socket
        self.safety_distance = safety_distance

        # Rotate sensor to starting position
        starting_orientation = view_angle // 2
        self.socket.send(f"ROTATESENSOR {starting_orientation}")
        self.orientation = geometry.Angle(0)
        self.rotate(starting_orientation)
        time.sleep(2)  # Wait until physical sensor is actually turned

    def scan(self):
        logging.info("Scanning started")
        num_steps = self.view_angle // self.precision + 1
        increasing = self.orientation.in_degrees() < 0

        @ssocket.handle_socket_error
        def loop():
            self.socket.send(f"SCAN {self.precision} {num_steps} {increasing}")
            while (data := self.socket.receive()) != "END":
                angle, measurement, *rest = data.split(" ")
                angle = float(angle)
                if not increasing:
                    angle = -angle
                measurement = float(measurement)
                if len(rest) > 0 and rest[0] == "FREE":
                    otype = ObservationType.FREE
                    measurement -= self.safety_distance
                else:
                    otype = ObservationType.OBSTACLE

                polar_angle = self.orientation.in_degrees() + angle
                polar = geometry.Polar(polar_angle, measurement)
                data = SensorMeasurement(polar, otype)
                self.data_queue.put(data)
        loop()

        total_rotation = (num_steps - 1) * self.precision
        if not increasing:
            total_rotation = -total_rotation
        self.rotate(total_rotation)

        self.data_queue.put(None)
        logging.info("Scanning finished")

    def rotate(self, angle):
        self.orientation.change(angle)


class SensorMeasurement():
    """
    polar: location of observation wrt. sensor coordinate system
    """
    def __init__(self, polar: geometry.Polar, otype: ObservationType):
        self.polar = polar
        self.type = otype
