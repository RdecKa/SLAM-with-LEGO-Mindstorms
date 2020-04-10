import logging
import os
import queue
import time

import slam.agent.robot as robot
import slam.display.map as smap
from slam.common.enums import Message, RobotType
from slam.config import config


def run():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    rtype = RobotType.SIMULATED

    config.setup(rtype)

    save = config.SAVE
    filename = None

    if save:
        save_folder = f"{config.SAVE_FOLDER}/" \
                      f"{time.strftime('%Y-%m-%d_%H-%M-%S')}"
        try:
            os.mkdir(save_folder)
            filename = f"{save_folder}/{config.SAVE_FILENAME_PREFIX}"
        except OSError:
            logging.error("Could not create a directory. Images will not be "
                          "saved")
            save = False

    robot_size = config.ROBOT_SIZE
    map = smap.Map(robot_size=robot_size, filename=filename,
                   save_params=config.SAVE_PARAMS)
    data_queue = queue.Queue()

    args = [
        data_queue,
    ]
    kwargs = {
        "robot_size": config.ROBOT_SIZE,
        "scanning_precision": config.SCANNING_PRECISION,
        "view_angle": config.VIEW_ANGLE,
    }

    if rtype == RobotType.SIMULATED:
        kwargs["world_number"] = config.WORLD_NUMBER
        kwargs["limited_view"] = config.LIMITED_VIEW
        agent = robot.SimulatedRobot(*args, **kwargs)
    elif rtype == RobotType.LEGO:
        agent = robot.LegoRobot(*args, **kwargs)
    else:
        raise TypeError
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
            map.redraw(save=save)
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
