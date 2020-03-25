from __future__ import annotations

import numpy as np


class Point():
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

    def __getitem__(self, key: int):
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise IndexError("Only indices 0 and 1 are accepted")

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def change(self, x: float, y: float):
        self.x += x
        self.y += y

    def plus_polar(self, polar: Polar) -> Point:
        cartesian = polar.to_cartesian()
        return self + cartesian


class Polar():
    def __init__(self, angle: int, radius: float):
        self.angle = Angle(angle)
        self.radius = radius

    def __str__(self):
        return f"<{self.angle}, {self.radius}>"

    def to_cartesian(self) -> Point:
        x = self.radius * np.cos(self.angle.in_radians())
        y = self.radius * np.sin(self.angle.in_radians())
        return Point(x, y)


class Angle():
    def __init__(self, angle: int):
        self.angle = angle

    def __str__(self):
        return f"{self.angle}°"

    def change(self, angle: int):
        self.angle += angle
        self.angle %= 360

    def in_degrees(self) -> int:
        return self.angle

    def in_radians(self) -> float:
        return np.radians(self.angle)


class Pose():
    def __init__(self, x: float, y: float, angle: int):
        self.position = Point(x, y)
        self.orientation = Angle(angle)

    def __str__(self):
        return f"{self.position}, {self.orientation}"

    def __getitem__(self, key: int):
        if not isinstance(key, int):
            raise TypeError("Wrong key type")
        if key == 0:
            return self.position.x
        if key == 1:
            return self.position.y
        if key == 2:
            return self.orientation.in_degrees()
        raise IndexError("Only indices in [0, 1, 2] are accepted")

    def rotate(self, angle: int):
        self.orientation.change(angle)

    def move_forward(self, distance: float):
        x = distance * np.cos(self.orientation.in_radians())
        y = distance * np.sin(self.orientation.in_radians())
        self.position.change(x, y)

    def get_position(self) -> Point:
        return self.position
