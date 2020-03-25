import matplotlib.pyplot as plt
import numpy as np

plt.ion()


class Map():
    def __init__(self):
        self.data = np.empty([0, 2])
        self.cdata = np.empty([0, 4])
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.scat = self.ax.scatter([], [])

    def redraw(self):
        # Update data
        self.scat.remove()
        self.scat = self.ax.scatter(self.data[:, 0], self.data[:, 1],
                                    c=self.cdata)
        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, data):
        self.data = np.vstack((self.data, (data.x, data.y)))
        self.cdata = np.vstack((self.cdata, data.color))
