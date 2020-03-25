import numpy as np


class Point():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def change(self, x: float, y: float):
        self.x += x
        self.y += y


class Angle():
    def __init__(self, angle: int):
        self.angle = angle

    def change(self, angle: int):
        self.angle += angle

    def in_degrees(self) -> int:
        return self.angle

    def in_radians(self) -> float:
        return np.radians(self.angle)


class Pose():
    def __init__(self, x: float, y: float, angle: int):
        self.position = Point(x, y)
        self.orientation = Angle(angle)

    def rotate(self, angle: int):
        self.orientation.change(angle)

    def move_forward(self, distance: float):
        x = distance * np.cos(self.orientation.in_radians())
        y = distance * np.sin(self.orientation.in_radians())
        self.position.change(x, y)

    def get_coordinates(self) -> int:
        return (self.position.x, self.position.y)
