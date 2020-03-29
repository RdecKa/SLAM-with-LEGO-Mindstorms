import queue

import slam.common.datapoint as datapoint
import slam.world.observed as oworld


class Planner():
    def __init__(self, observed_world: oworld.ObservedWorld,
                 data_queue: queue.Queue):
        self.observed_world = observed_world
        self.data_queue = data_queue

    def select_next_position(self):
        predicted_world, origin = self.observed_world.predict_world()
        if predicted_world is None or origin is None:
            return
        self.data_queue.put(datapoint.Prediction(*origin, predicted_world))
        # TODO
