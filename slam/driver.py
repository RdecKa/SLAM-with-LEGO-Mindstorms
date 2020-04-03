import logging
import queue
import time

import slam.agent.robot as robot
import slam.display.map as smap
from slam.common.enums import Message


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    map = smap.Map()
    data_queue = queue.Queue()
    agent = robot.LegoRobot(data_queue, scanning_precision=30, view_angle=300)
    agent.start()

    try:
        while agent.is_alive():
            try:
                data = data_queue.get(timeout=3)
            except queue.Empty:
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
