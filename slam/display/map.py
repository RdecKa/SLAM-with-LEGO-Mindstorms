import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.path as mpath

import slam.common.datapoint as datapoint

plt.ion()


class Map():
    def __init__(self, draw_path: bool = True):
        self.data = np.empty([0, 2])
        self.color_data = np.empty([0, 4])
        self.draw_path = draw_path
        if draw_path:
            self.path_data = np.empty([0, 2])
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.scat = None
        self.path = None

    def redraw(self):
        # Update data
        if self.scat:
            self.scat.remove()
        self.scat = self.ax.scatter(self.data[:, 0], self.data[:, 1],
                                    c=self.color_data)

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
        self.data = np.vstack((self.data, [*data.location]))
        self.color_data = np.vstack((self.color_data, data.color))
        if self.draw_path and isinstance(data, datapoint.Pose):
            self.path_data = np.vstack((self.path_data, [*data.location]))

    def compute_path_codes(self):
        if (len(self.path_data) == 0):
            return []
        return [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(self.path_data) - 1)
