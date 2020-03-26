from typing import Dict, List

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.world.world as world


class ObservedWorld(world.World):
    def __init__(self):
        self.map: Dict[geometry.Point, List[datapoint.Observation]] = dict()

    def add_observation(self, pose: datapoint.Pose,
                        observation: datapoint.Observation):
        if pose.location in self.map:
            self.map[pose.location].append(observation)
        else:
            self.map[pose.location] = [observation]
