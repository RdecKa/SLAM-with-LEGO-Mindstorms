import matplotlib.pyplot as plt

plt.ion()


class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.xdata = []
        self.ydata = []
        self.init_graph()

    def init_graph(self):
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([], [], 'o')

    def redraw(self):
        # Update data
        self.lines.set_xdata(self.xdata)
        self.lines.set_ydata(self.ydata)
        # Rescale
        self.ax.relim()
        self.ax.autoscale_view()
        # Draw and flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def add_data(self, x, y):
        self.xdata.append(x)
        self.ydata.append(y)
