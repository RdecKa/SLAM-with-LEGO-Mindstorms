from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

import slam.common.datapoint as datapoint
from slam.common.enums import Existence, PathId


class MapStorage():
    def __init__(self, draw_path=True):
        self.draw_path = draw_path
        self.scatter_storage = ScatterStorage()
        self.heatmap_storage = HeatmapStorage()
        if draw_path:
            self.path_storage = PathStorage()

    def get_scatter_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.scatter_storage.get_data()

    def get_heatmap_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.heatmap_storage.get_data()

    def get_path_data(self) -> Dict[PathId, PathStorageEntry]:
        return self.path_storage.get_data()

    def add_scatter_data(self, data: datapoint.DataPoint):
        self.scatter_storage.add_data(data)

    def add_heatmap_data(self, data: datapoint.DataPoint):
        self.heatmap_storage.set_data(data)

    def add_path_data(self, data: datapoint.DataPoint):
        self.path_storage.add_data(data)

    def delete_temporary_data(self):
        self.scatter_storage.delete_temporary_data()
        if self.draw_path:
            self.path_storage.delete_temporary_data()


class ScatterStorage():
    def __init__(self):
        self.data = {e: ScatterStorageEntry() for e in Existence}

    def add_data(self, data: datapoint.DataPoint):
        self.data[data.existence].add_data(data)

    def get_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        data = np.vstack([self.data[e].get_data() for e in Existence])
        x_data = data[:, 0]
        y_data = data[:, 1]
        c_data = data[:, 2:6]
        return (x_data, y_data, c_data)

    def delete_temporary_data(self):
        self.data[Existence.TEMPORARY] = ScatterStorageEntry()


class ScatterStorageEntry():
    def __init__(self):
        """
        0, 1: x, y coordinate
        2 - 5: color (RGBA)
        """
        self.data = np.empty([0, 6])

    def add_data(self, data: datapoint.DataPoint):
        self.data = np.vstack((self.data, [*data.location, *data.color]))

    def get_data(self):
        return self.data


class HeatmapStorage():
    def __init__(self):
        """
        0, 1: x, y coordinate
        2: weight
        """
        self.data = np.empty([0, 3])

    def set_data(self, data: datapoint.DataPoint):
        self.data = np.empty([0, 3])
        origin_x, origin_y = *data.location,
        for iy in range(len(data.predicted_world)):
            for ix in range(len(data.predicted_world[iy])):
                d = data.predicted_world[iy][ix]
                x = ix + origin_x
                y = iy + origin_y
                self.data = np.vstack((self.data, (x, y, d)))

    def get_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x_data = self.data[:, 0]
        y_data = self.data[:, 1]
        w_data = self.data[:, 2]
        return (x_data, y_data, w_data)


class PathStorage():
    def __init__(self):
        self.data = dict()

    def add_data(self, data: datapoint.DataPoint):
        if data.path_id is None:
            logging.warning("Received path data without path_id")
            return

        if data.path_id not in self.data:
            self.data[data.path_id] = PathStorageEntry(data.path_style,
                                                       data.existence)
        self.data[data.path_id].add_data(data)

    def get_data(self) -> Dict[PathId, PathStorageEntry]:
        return self.data

    def delete_temporary_data(self):
        for path_id in self.data:
            if self.data[path_id].existence == Existence.TEMPORARY:
                linestyle = self.data[path_id].linestyle
                self.data[path_id] = PathStorageEntry(linestyle,
                                                      Existence.TEMPORARY)


class PathStorageEntry():
    def __init__(self, linestyle: str = "-",
                 existence: Existence = Existence.PERMANENT):
        """
        0, 1: x, y coordinate
        """
        self.linestyle = linestyle
        self.data = np.empty([0, 2])
        self.existence = existence

    def add_data(self, new_data: datapoint.DataPoint):
        self.data = np.vstack((self.data, [*new_data.location]))
