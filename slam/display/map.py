import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

import slam.common.datapoint as datapoint
import slam.display.storage as storage
from slam.common.enums import GraphType, Message

plt.ion()


class Map():
    def __init__(self, draw_path: bool = True):
        self.storage = storage.MapStorage(draw_path)
        self.draw_path = draw_path
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots(figsize=(7, 7))
        self.scat = None
        self.path = dict()
        self.heat = None

    def redraw(self):
        # Heatmap
        x_heat, y_heat, w_heat = self.storage.get_heatmap_data()
        if x_heat.size > 0:
            if self.heat:
                self.heat[3].remove()
                del self.heat

            x_max, x_min = max(x_heat), min(x_heat)
            y_max, y_min = max(y_heat), min(y_heat)
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
            self.heat = self.ax.hist2d(x_heat, y_heat, weights=w_heat,
                                       bins=bins, range=map_range, cmap="BrBG",
                                       alpha=.3, vmin=-10, vmax=10)

        # Scatter plot
        if self.scat:
            self.scat.remove()
            del self.scat

        x_scat, y_scat, c_scat = self.storage.get_scatter_data()
        self.scat = self.ax.scatter(x_scat, y_scat, c=c_scat)

        # Path
        if self.draw_path:
            path_data = self.storage.get_path_data()
            for path_id in path_data:
                if path_id in self.path and self.path[path_id]:
                    self.path[path_id].remove()
                path_data_entry = path_data[path_id]
                codes = self.compute_path_codes(path_data_entry.data)
                path = mpath.Path(path_data_entry.data, codes)
                patch = patches.PathPatch(path, fill=False, lw=1,
                                          ls=path_data_entry.linestyle)
                self.path[path_id] = self.ax.add_patch(patch)

        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

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
