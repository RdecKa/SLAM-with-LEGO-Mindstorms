import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.path as mpath


plt.ion()


class Map():
    def __init__(self, draw_path: bool = True):
        self.data = np.empty([0, 2])
        self.cdata = np.empty([0, 4])
        self.draw_path = draw_path
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
                                    c=self.cdata)

        if self.draw_path:
            if self.path:
                self.path.remove()
            path = mpath.Path(self.data, self.compute_path_codes())
            patch = patches.PathPatch(path, fill=False, lw=1)
            self.path = self.ax.add_patch(patch)

        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, data):
        self.data = np.vstack((self.data, (data.x, data.y)))
        self.cdata = np.vstack((self.cdata, data.color))

    def compute_path_codes(self):
        if (len(self.data) == 0):
            return []
        return [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(self.data) - 1)
