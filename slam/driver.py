import logging
import queue
import time

import slam.agent.robot as robot
import slam.display.map as smap
from slam.common.enums import Message


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    robot_size = 10.0
    map = smap.Map(robot_size=robot_size)
    data_queue = queue.Queue()

    args = [
        data_queue,
    ]
    kwargs = {
        "robot_size": robot_size,
        "scanning_precision": 20,
        "view_angle": 330,
        "world_number": 5,
        "limited_view": 20.0,
    }
    agent = robot.SimulatedRobot(*args, **kwargs)
    agent.start()

    try:
        while agent.is_alive():
            try:
                data = data_queue.get(timeout=3)
            except queue.Empty:
                map.redraw()
                continue

            if isinstance(data, Message):
                map.handle_message(data)
            else:
                map.add_data(data)
                map.redraw()
    except KeyboardInterrupt:
        pass

    agent.shutdown_flag.set()
    agent.join()

    try:
        logging.info("Waiting for KeyboardInterrupt")
        while True:
            map.redraw()
            time.sleep(3)
    except KeyboardInterrupt:
        pass
