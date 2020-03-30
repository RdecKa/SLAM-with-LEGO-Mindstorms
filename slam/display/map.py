import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np

import slam.common.datapoint as datapoint
from slam.common.enums import GraphType

plt.ion()


class Map():
    def __init__(self, draw_path: bool = True):
        self.data = dict()
        self.init_scatter_data()
        self.init_heatmap_data()
        self.draw_path = draw_path
        if draw_path:
            self.path_data = np.empty([0, 2])
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.scat = None
        self.path = None
        self.heat = None

    def init_scatter_data(self):
        self.data[GraphType.SCATTER.name] = [np.empty([0, 2]), np.empty([0, 4])]

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
            bins = max(1, int(np.min([x_diff, y_diff, 50])))
            self.heat = self.ax.hist2d(data[:, 0], data[:, 1],
                                       weights=data[:, 2], bins=bins,
                                       cmap="BrBG", alpha=.3, vmin=-10,
                                       vmax=10)

        # Scatter plot
        if self.scat:
            self.scat.remove()
            del self.scat

        data = self.data[GraphType.SCATTER.name][0]
        c = self.data[GraphType.SCATTER.name][1]
        self.scat = self.ax.scatter(data[:, 0], data[:, 1], c=c)

        # Path
        if self.draw_path:
            if self.path:
                self.path.remove()
            path = mpath.Path(self.path_data, self.compute_path_codes())
            patch = patches.PathPatch(path, fill=False, lw=1)
            self.path = self.ax.add_patch(patch)

        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, data: datapoint.DataPoint):
        if data.graph_type == GraphType.SCATTER:
            self.data[GraphType.SCATTER.name][0] = np.vstack((
                self.data[GraphType.SCATTER.name][0],
                [*data.location]
            ))
            self.data[GraphType.SCATTER.name][1] = np.vstack((
                self.data[GraphType.SCATTER.name][1],
                data.color
            ))
            if self.draw_path and isinstance(data, datapoint.Pose):
                self.path_data = np.vstack((self.path_data, [*data.location]))
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

    def compute_path_codes(self):
        if (len(self.path_data) == 0):
            return []
        return [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(self.path_data) - 1)
