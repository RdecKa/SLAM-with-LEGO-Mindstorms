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

    def __eq__(self, other: Point) -> bool:
        eps = 1e-6
        return abs(self.x - other.x) < eps and abs(self.y - other.y) < eps

    def __hash__(self):
        return hash((self.x, self.y))

    def change(self, x: float = 0, y: float = 0):
        self.x += x
        self.y += y

    def plus_polar(self, polar: Polar) -> Point:
        cartesian = polar.to_cartesian()
        return self + cartesian

    def distance_to(self, other: Point) -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_to(self, point: Point):
        x = point.x - self.x
        y = point.y - self.y
        if abs(x) < 1e-6 and abs(y) < 1e-6:
            return Angle(0)
        angle = np.degrees(np.arctan2(y, x))
        return Angle(angle)


class Polar():
    def __init__(self, angle: int, radius: float):
        if radius < 0:
            raise ValueError
        self.angle = Angle(angle)
        self.radius = radius

    def __str__(self):
        return f"<{self.angle}, {self.radius:.2f}>"

    def change(self, angle: Angle, radius: int = 0):
        self.angle.change(angle)
        self.radius += radius
        if self.radius < 0:
            raise ValueError

    def to_cartesian(self) -> Point:
        x = self.radius * np.cos(self.angle.in_radians())
        y = self.radius * np.sin(self.angle.in_radians())
        return Point(x, y)


class Angle():
    def __init__(self, angle: int):
        self.angle = angle
        self.transform_to_range()

    def __str__(self):
        return f"{self.angle:.2f}°"

    def __add__(self, other: Angle):
        return Angle(self.angle + other.angle)

    def __sub__(self, other: Angle):
        return Angle(self.angle - other.angle)

    def change(self, angle: int):
        self.angle += angle
        self.transform_to_range()

    def in_degrees(self) -> int:
        return self.angle

    def in_radians(self) -> float:
        return np.radians(self.angle)

    def transform_to_range(self):
        """
        Transform in range (-180°, 180°]
        """
        self.angle %= 360
        if self.angle > 180:
            self.angle -= 360


class Pose():
    def __init__(self, x: float, y: float, angle: int = 0):
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

    def turn_towards(self, point: Point):
        angle = self.angle_to_point(point).in_degrees()
        self.rotate(angle)

    def angle_to_point(self, point: Point):
        x = point.x - self.position.x
        y = point.y - self.position.y
        if x == 0 and y == 0:
            return Angle(0)
        angle_of_point = self.position.angle_to(point)

        return angle_of_point - self.orientation
