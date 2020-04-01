import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

import slam.common.datapoint as datapoint
from slam.common.enums import Existence, GraphType, Message, PathId

plt.ion()


class Map():
    def __init__(self, draw_path: bool = True):
        self.data = dict()
        self.init_scatter_data()
        self.init_heatmap_data()
        self.draw_path = draw_path
        if draw_path:
            self.path_data = {
                path_id: [np.empty([0, 2]), "-"] for path_id in PathId}
            self.path = dict()
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.scat = None
        self.path = dict()
        self.heat = None

    def init_scatter_data(self):
        self.data[GraphType.SCATTER.name] = {
            e.name: [np.empty([0, 2]), np.empty([0, 4])] for e in Existence}

    def init_heatmap_data(self):
        self.data[GraphType.HEATMAP.name] = np.empty([0, 3])

    def redraw(self):
        # Heatmap
        if self.data[GraphType.HEATMAP.name].size > 0:
            if self.heat:
                self.heat[3].remove()
                del self.heat

            data = self.data[GraphType.HEATMAP.name]
            x_diff = max(data[:, 0]) - min(data[:, 0])
            y_diff = max(data[:, 1]) - min(data[:, 1])
            bins = max(1, int(np.min([x_diff, y_diff, 60])))
            self.heat = self.ax.hist2d(data[:, 0], data[:, 1],
                                       weights=data[:, 2], bins=bins,
                                       cmap="BrBG", alpha=.3, vmin=-10,
                                       vmax=10)

        # Scatter plot
        if self.scat:
            self.scat.remove()
            del self.scat

        data = np.vstack(
            [self.data[GraphType.SCATTER.name][e.name][0] for e in Existence])
        c = np.vstack(
            [self.data[GraphType.SCATTER.name][e.name][1] for e in Existence])
        self.scat = self.ax.scatter(data[:, 0], data[:, 1], c=c)

        # Path
        if self.draw_path:
            for path_id in self.path_data:
                if path_id in self.path and self.path[path_id]:
                    self.path[path_id].remove()
                data = self.path_data[path_id]
                codes = self.compute_path_codes(data[0])
                path = mpath.Path(data[0], codes)
                patch = patches.PathPatch(path, fill=False, lw=1, ls=data[1])
                self.path[path_id] = self.ax.add_patch(patch)

        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, data: datapoint.DataPoint):
        if data.graph_type == GraphType.SCATTER:
            for d in data:
                self.data[GraphType.SCATTER.name][d.existence.name][0] = \
                    np.vstack((
                        self.data[GraphType.SCATTER.name][d.existence.name][0],
                        [*d.location]
                    ))
                self.data[GraphType.SCATTER.name][d.existence.name][1] = \
                    np.vstack((
                        self.data[GraphType.SCATTER.name][d.existence.name][1],
                        d.color
                    ))
                if self.draw_path and data.path_id is not None:
                    self.path_data[data.path_id][0] = np.vstack(
                        (self.path_data[data.path_id][0], [*data.location]))
                    self.path_data[data.path_id][1] = data.path_style
        elif data.graph_type == GraphType.HEATMAP:
            heatmap_data = np.empty([0, 3])
            origin_x, origin_y = *data.location,
            for iy in range(len(data.predicted_world)):
                for ix in range(len(data.predicted_world[iy])):
                    d = data.predicted_world[iy][ix]
                    x = ix + origin_x
                    y = iy + origin_y
                    heatmap_data = np.vstack((heatmap_data, (x, y, d)))
            self.data[GraphType.HEATMAP.name] = heatmap_data
        else:
            raise TypeError(f"Unknown graph type {data.graph_type}")

    def handle_message(self, msg: Message):
        if msg == Message.DELETE_TEMPORARY_DATA:
            self.data[GraphType.SCATTER.name][Existence.TEMPORARY.name] = \
                [np.empty([0, 2]), np.empty([0, 4])]
            if self.draw_path:
                self.path_data[PathId.ROBOT_PATH_PLAN] = [np.empty([0, 2]),
                                                          "--"]
        else:
            raise TypeError(f"Unknown Message type {msg}")

    def compute_path_codes(self, path_data):
        if (len(path_data) == 0):
            return []
        return [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(path_data) - 1)
