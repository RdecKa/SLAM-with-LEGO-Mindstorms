import logging
import queue

import slam.agent.robot as robot
import slam.common.geometry as geometry
import slam.display.map as smap


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    map = smap.Map()
    origin = geometry.Pose(5, 40, -45)
    data_queue = queue.Queue()
    agent = robot.SimulatedRobot(data_queue, origin, scanning_precision=30,
                                 view_angle=360)
    agent.start()

    try:
        while True:
            data = data_queue.get()
            map.add_data(data)
            map.redraw()
    except KeyboardInterrupt:
        pass

    agent.shutdown_flag.set()
    agent.join()
