import unittest

import numpy as np

import slam.common.geometry as geometry


class TestPoint(unittest.TestCase):
    def test_creation(self):
        p = geometry.Point(3, 5)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 5)

    def test_str(self):
        p = geometry.Point(3, 5)
        self.assertEqual(str(p), "(3.00, 5.00)")

    def test_getitem(self):
        p = geometry.Point(3, 5)
        self.assertEqual(p[0], p.x)
        self.assertEqual(p[1], p.y)
        with self.assertRaises(TypeError):
            p["not integer"]
        for index in [-1, 2]:
            with self.assertRaises(IndexError):
                p[index]

    def test_add(self):
        p1 = geometry.Point(3, 5)
        p2 = geometry.Point(2, 1)
        p3 = p1 + p2
        self.assertEqual(p3.x, 5)
        self.assertEqual(p3.y, 6)

    def test_eq(self):
        p1 = geometry.Point(3, 5)
        p2 = geometry.Point(3, 5)
        self.assertEqual(p1, p2)

    def test_eq_float(self):
        p1 = geometry.Point(3.00000005, 5.000000001)
        p2 = geometry.Point(3, 5)
        self.assertEqual(p1, p2)

    def test_change(self):
        p = geometry.Point(3, 5)
        p.change(2.5, 1.1)
        self.assertAlmostEqual(p.x, 5.5)
        self.assertAlmostEqual(p.y, 6.1)

    def test_change_negative(self):
        p = geometry.Point(3, 5)
        p.change(-5.0, -0.5)
        self.assertAlmostEqual(p.x, -2)
        self.assertAlmostEqual(p.y, 4.5)

    def test_plus_polar(self):
        cart = geometry.Point(3, 5)

        def test_helper(angle, radius, expected_x, expected_y):
            polar = geometry.Polar(angle, radius)
            result = cart.plus_polar(polar)
            self.assertAlmostEqual(result.x, expected_x)
            self.assertAlmostEqual(result.y, expected_y)

        test_helper(0, 1, 4, 5)
        test_helper(90, 1, 3, 6)
        test_helper(180, 4, -1, 5)
        test_helper(-90, 2, 3, 3)
        test_helper(45, np.sqrt(2), 4, 6)
        test_helper(120, 3, 3 + 3 * np.cos(np.radians(120)),
                    5 + 3 * np.sin(np.radians(120)))
        test_helper(-120, 3, 1.5, 5 + 3 * np.sin(np.radians(-120)))

    def test_distance_to(self):
        def test_helper(x, y, other_x, other_y, expected_distance):
            p1 = geometry.Point(x, y)
            p2 = geometry.Point(other_x, other_y)
            d1 = p1.distance_to(p2)
            d2 = p2.distance_to(p1)
            self.assertAlmostEqual(d1, d2)
            self.assertAlmostEqual(d1, expected_distance)

        test_helper(5, 5, 7, 5, 2)
        test_helper(-2, 7, 0, 5, np.sqrt(8))
        test_helper(5, 4, 5, 4, 0)

    def test_angle_to(self):
        def test_helper(x, y, other_x, other_y, expected_angle):
            p1 = geometry.Point(x, y)
            p2 = geometry.Point(other_x, other_y)
            a = p1.angle_to(p2).in_degrees()
            self.assertAlmostEqual(a, expected_angle)

        test_helper(1, 1, 5, 5, 45)
        test_helper(1, 1, 0, 2, 135)
        test_helper(1, 1, -1, -1, -135)
        test_helper(1, 1, 3, -1, -45)
        test_helper(5, 5, 6, 5, 0)
        test_helper(5, 5, -6, 5, 180)
        test_helper(-2, -2, -2, 1, 90)
        test_helper(-2, -2, -2, -5, -90)


class TestPolar(unittest.TestCase):
    def test_creation(self):
        p = geometry.Polar(45, 5.)
        self.assertAlmostEqual(p.angle.in_degrees(), 45)
        self.assertAlmostEqual(p.radius, 5.)

    def test_creation_invalid(self):
        with self.assertRaises(ValueError):
            geometry.Polar(45, -5.)

    def test_str(self):
        p = geometry.Polar(45, 5.)
        self.assertEqual(str(p), "<45.00°, 5.00>")

    def test_change(self):
        p = geometry.Polar(45, 5.)
        p.change(20, 1)
        self.assertAlmostEqual(p.angle.in_degrees(), 65)
        self.assertAlmostEqual(p.radius, 6.)

    def test_change_negative(self):
        p = geometry.Polar(45, 5.)
        p.change(-90, -2.)
        self.assertAlmostEqual(p.angle.in_degrees(), -45)
        self.assertAlmostEqual(p.radius, 3.)

    def test_change_negative_invalid(self):
        p = geometry.Polar(45, 5.)
        with self.assertRaises(ValueError):
            p.change(-90, -9.)

    def test_to_cartesian(self):
        def test_helper(angle, radius, expected_x, expected_y):
            polar = geometry.Polar(angle, radius)
            cart = polar.to_cartesian()
            self.assertAlmostEqual(cart.x, expected_x)
            self.assertAlmostEqual(cart.y, expected_y)

        test_helper(0, 5., 5., 0)
        test_helper(90, 2, 0, 2)
        test_helper(-180, 0.0001, -0.0001, 0)
        test_helper(-90, 4.5, 0, -4.5)
        test_helper(45, 3 * np.sqrt(2), 3, 3)
        test_helper(30, 4, 4 * np.cos(np.radians(30)), 2)
        test_helper(170, 2.5, 2.5 * np.cos(np.radians(170)),
                    2.5 * np.sin(np.radians(170)))


class TestAngle(unittest.TestCase):
    def test_creation(self):
        a = geometry.Angle(5)
        self.assertAlmostEqual(a.angle, 5)

    def test_str(self):
        a = geometry.Angle(5)
        self.assertEqual(str(a), "5.00°")

    def test_add(self):
        def test_helper(angle_1, angle_2, expected_angle):
            a1 = geometry.Angle(angle_1)
            a2 = geometry.Angle(angle_2)
            s1 = a1 + a2
            s2 = a2 + a1
            self.assertAlmostEqual(s1.in_degrees(), s2.in_degrees())
            self.assertAlmostEqual(s1.in_degrees(), expected_angle)

        test_helper(20, 20, 40)
        test_helper(20, -20, 0)
        test_helper(-15, 55, 40)
        test_helper(170, 20, -170)
        test_helper(-160, -30, 170)

    def test_sub(self):
        def test_helper(angle_1, angle_2, expected_angle):
            a1 = geometry.Angle(angle_1)
            a2 = geometry.Angle(angle_2)
            s = a1 - a2
            self.assertAlmostEqual(s.in_degrees(), expected_angle)

        test_helper(50, 20, 30)
        test_helper(0, 20, -20)
        test_helper(13, -15, 28)
        test_helper(-20, 40, -60)
        test_helper(-175, 5, 180)
        test_helper(-175, 180, 5)

    def test_change(self):
        a = geometry.Angle(5)
        a.change(10)
        self.assertAlmostEqual(a.angle, 15)
        a.change(-35)
        self.assertAlmostEqual(a.angle, -20)
        a.change(100)
        self.assertAlmostEqual(a.angle, 80)

    def test_in_degrees(self):
        a = geometry.Angle(5)
        d = a.in_degrees()
        self.assertAlmostEqual(d, 5)

    def test_in_radians(self):
        a = geometry.Angle(5)
        r = a.in_radians()
        self.assertAlmostEqual(r, np.radians(5))

    def test_in_radians_negative(self):
        a = geometry.Angle(-165)
        r = a.in_radians()
        self.assertAlmostEqual(r, np.radians(-165))


class TestPose(unittest.TestCase):
    def test_creation(self):
        p = geometry.Pose(5.5, 9.9, 100)
        self.assertAlmostEqual(p.position.x, 5.5)
        self.assertAlmostEqual(p.position.y, 9.9)
        self.assertAlmostEqual(p.orientation.in_degrees(), 100)

    def test_str(self):
        p = geometry.Pose(5.5555, 9.9999, 100)
        self.assertEqual(str(p), "(5.56, 10.00), 100.00°")

    def test_getitem(self):
        p = geometry.Pose(-5.12, 10.598, -50)
        self.assertEqual(p[0], p.position.x)
        self.assertEqual(p[1], p.position.y)
        self.assertEqual(p[2], p.orientation.in_degrees())
        with self.assertRaises(TypeError):
            p["not integer"]
        for index in [-1, 3]:
            with self.assertRaises(IndexError):
                p[index]

    def test_rotate(self):
        p = geometry.Pose(5, 4, 45)
        p.rotate(50)
        self.assertAlmostEqual(p.orientation.in_degrees(), 95)
        p.rotate(300)
        self.assertAlmostEqual(p.orientation.in_degrees(), 35)
        p.rotate(-65)
        self.assertAlmostEqual(p.orientation.in_degrees(), -30)

    def test_move_forward_up(self):
        p = geometry.Pose(-4, 2, 90)
        p.move_forward(5)
        self.assertAlmostEqual(p.position.x, -4)
        self.assertAlmostEqual(p.position.y, 7)

    def test_move_forward_left(self):
        p = geometry.Pose(-4, 2, 180)
        p.move_forward(5)
        self.assertAlmostEqual(p.position.x, -9)
        self.assertAlmostEqual(p.position.y, 2)

    def test_move_forward_diagonal(self):
        p = geometry.Pose(-4, 2, 135)
        p.move_forward(5)
        self.assertAlmostEqual(p.position.x, -4 + 5 * np.cos(np.radians(135)))
        self.assertAlmostEqual(p.position.y, 2 + 5 * np.sin(np.radians(135)))

    def test_turn_towards(self):
        def test_helper(x, y, angle, remote_x, remote_y, expected_angle):
            p = geometry.Pose(x, y, angle)
            point = geometry.Point(remote_x, remote_y)
            p.turn_towards(point)
            self.assertAlmostEqual(p.orientation.in_degrees(), expected_angle)

        test_helper(0, 0, 0, 1, 1, 45)
        test_helper(0, 0, 90, -2, -2, -135)
        test_helper(0, 0, -180, -3, 3, 135)
        test_helper(2, 2, 180, -10, 2, 180)
        test_helper(-10, 1, 90, -10, -2, -90)
        test_helper(2, -2, 23, 8, 1, np.degrees(np.arctan2(3, 6)))

    def test_angle_to_point(self):
        def test_helper(x, y, angle, remote_x, remote_y, expected_angle):
            p = geometry.Pose(x, y, angle)
            point = geometry.Point(remote_x, remote_y)
            a = p.angle_to_point(point)
            self.assertAlmostEqual(a.in_degrees(), expected_angle)

        test_helper(0, 0, 0, 5, 5, 45)
        test_helper(-3, 2, 90, -1, 0, -135)
        test_helper(6, 6, -45, -6, -6, -90)
        test_helper(1, 1, 0, 4, 1 + 6 * np.sqrt(3) / 2, 60)
        test_helper(-5, -5, 180, 0, -5, 180)
        test_helper(-4, -4, 170, -4, -4, 0)
        test_helper(-4, -4, 170, -4, 0, -80)
