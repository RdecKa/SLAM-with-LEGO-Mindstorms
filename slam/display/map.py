import matplotlib.pyplot as plt
import numpy as np

plt.ion()


class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = np.empty([0, 2])
        self.cdata = np.empty([0, 4])
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.scat = self.ax.scatter([], [])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)

    def redraw(self):
        # Update data
        self.scat.set_offsets(self.data)
        self.scat.set_facecolors(self.cdata)
        # Rescale
        self.ax.relim()
        self.ax.autoscale_view()
        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, data):
        self.data = np.vstack((self.data, (data.x, data.y)))
        self.cdata = np.vstack((self.cdata, data.color))
