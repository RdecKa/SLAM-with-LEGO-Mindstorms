import logging
from typing import Dict

import matplotlib.collections as collections
import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.pyplot as plt

import slam.common.datapoint as datapoint
import slam.display.storage as storage
from slam.common.enums import GraphType, Message

plt.ion()


class Map():
    def __init__(self, robot_size: float = 10.0, draw_path: bool = True,
                 filename: str = None, save_params: Dict = None):
        self.storage = storage.MapStorage(draw_path)
        self.draw_path = draw_path
        self.robot_size = robot_size
        self.init_graph()
        self.filename = filename
        self.save_params = save_params
        self.file_count = 1

    def init_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(5, 5))
        self.scat = None
        self.path = dict()
        self.heat = None

    def redraw(self, save=False):
        # Heatmap
        x_heat, y_heat, w_heat = self.storage.get_heatmap_data()
        if x_heat.size > 0:
            if self.heat:
                self.heat[3].remove()
                del self.heat

            map_range, bins = self.calculate_params_for_heatmap(x_heat, y_heat)

            self.heat = self.ax.hist2d(x_heat, y_heat, weights=w_heat,
                                       bins=bins, range=map_range, cmap="BrBG",
                                       alpha=0.3, vmin=-10, vmax=10)

        # Scatter plot
        if self.scat:
            self.scat.remove()
            del self.scat

        x_scat, y_scat, c_scat = self.storage.get_scatter_data()
        self.scat = self.ax.scatter(x_scat, y_scat, c=c_scat)

        # Path and circles
        if self.draw_path:
            path_data = self.storage.get_path_data()
            for path_id in path_data:
                if path_id in self.path:
                    for p in self.path[path_id]:
                        if p:
                            p.remove()
                path_data_entry = path_data[path_id]
                self.path[path_id] = self.create_patches(path_data_entry)

        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

        if save:
            if not self.filename:
                logging.error("Filename missing")
            else:
                fmt = self.save_params["format"]
                name = f"{self.filename}{self.file_count:05d}.{fmt}"
                self.figure.savefig(name, **self.save_params)
                self.file_count += 1

    def calculate_params_for_heatmap(self, x_data, y_data):
        x_max, x_min = max(x_data), min(x_data)
        y_max, y_min = max(y_data), min(y_data)
        x_diff = x_max - x_min
        y_diff = y_max - y_min

        if x_diff > y_diff:
            x_margin = x_diff * 0.1
            total_size = x_diff + 2 * x_margin
            y_margin = (total_size - y_diff) / 2
        else:
            y_margin = y_diff * 0.1
            total_size = y_diff + 2 * y_margin
            x_margin = (total_size - x_diff) / 2

        map_range = [[x_min - x_margin, x_max + x_margin],
                     [y_min - y_margin, y_max + y_margin]]
        bins = int(min(max(1, x_diff, y_diff), 60))
        return map_range, bins

    def create_patches(self, path_data_entry: storage.PathStorageEntry):
        codes = self.compute_path_codes(path_data_entry.data)
        path = mpath.Path(path_data_entry.data, codes)
        path_patch = patches.PathPatch(path, fill=False, lw=1,
                                       ls=path_data_entry.linestyle)
        circle_patches = []
        for row in path_data_entry.data:
            circle = patches.Circle(row, radius=self.robot_size / 2)
            circle_patches.append(circle)

        collection = collections.PatchCollection(circle_patches, alpha=0.3,
                                                 color=(0.7, 0.7, 0.7))

        return [
            self.ax.add_patch(path_patch),
            self.ax.add_collection(collection),
        ]

    def add_data(self, data: datapoint.DataPoint):
        if data.graph_type == GraphType.SCATTER:
            for d in data:
                self.storage.add_scatter_data(d)
                if self.draw_path and data.path_id is not None:
                    self.storage.add_path_data(d)
        elif data.graph_type == GraphType.HEATMAP:
            self.storage.add_heatmap_data(data)
        else:
            raise TypeError(f"Unknown graph type {data.graph_type}")

    def handle_message(self, msg: Message):
        if msg == Message.DELETE_TEMPORARY_DATA:
            self.storage.delete_temporary_data()
        else:
            raise TypeError(f"Unknown Message type {msg}")

    def compute_path_codes(self, path_data):
        if (len(path_data) == 0):
            return []
        return [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(path_data) - 1)
