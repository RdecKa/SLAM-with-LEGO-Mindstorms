import logging
import queue

import slam.agent.robot as robot
import slam.common.geometry as geometry
import slam.display.map as smap
from slam.common.enums import Message


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    map = smap.Map()
    origin = geometry.Pose(25, 5, 45)
    data_queue = queue.Queue()
    agent = robot.SimulatedRobot(data_queue, origin, scanning_precision=30,
                                 view_angle=360)
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
