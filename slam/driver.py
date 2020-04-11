import logging
import queue
import time

import slam.agent.robot as robot
import slam.display.map as smap
from slam.common.enums import Message, RobotType
from slam.config import config


def init_robot(rtype: RobotType, data_queue: queue.Queue) -> robot.Robot:
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

    return agent


def run(rtype: RobotType, save: bool = False, filename: str = None):
    map = smap.Map(robot_size=config.ROBOT_SIZE, filename=filename,
                   save_params=config.SAVE_PARAMS)
    data_queue = queue.Queue()
    agent = init_robot(rtype, data_queue)
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
            time.sleep(1)
    except KeyboardInterrupt:
        pass
