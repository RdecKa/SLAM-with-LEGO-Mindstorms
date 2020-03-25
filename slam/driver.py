import logging
import queue

import slam.agent.robot as robot
import slam.display.map as smap


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    map = smap.Map()
    data_queue = queue.Queue()
    agent = robot.Robot(data_queue)
    agent.start()

    try:
        while True:
            if not data_queue.empty():
                data = data_queue.get()
                map.add_data(data)
                map.redraw()
    except KeyboardInterrupt:
        pass

    agent.shutdown_flag.set()
    agent.join()
