#coding:utf-8
import unittest
import math
class TestVector(unittest.TestCase):
    def setUp(self):
        pass

    def test_vector_get_and_set(self):
        x = 30
        y = 40
        v = Canvas.Vector(x, y)
        self.assertEqual(v.get_x(), x)
        self.assertEqual(v.get_y(), y)

    def test_vector_get_angle_and_length(self):
        x = 30
        y = 40
        v = Canvas.Vector(x, y)
        self.assertEqual(v.get_angle(), math.atan(y / x))
        self.assertEqual(v.get_length(), math.hypot(x, y))

    def test_vector_change_x_and_y(self):
        x = 0
        y = 0
        v = Canvas.Vector(x, y)
        self.assertEqual(v.get_angle(), 0)
        self.assertEqual(v.get_length(), 0)
        v.set_y(30)
        self.assertEqual(v.get_angle(), math.pi / 2)
        self.assertEqual(v.get_length(), 30)
        v.set_y(-30)
        self.assertEqual(v.get_angle(), -math.pi / 2)
        self.assertEqual(v.get_length(), 30)
        v.set_y(0)
        v.set_x(50)
        self.assertEqual(v.get_angle(), 0)
        self.assertEqual(v.get_length(), 50)
        v.set_x(-50)
        self.assertEqual(v.get_angle_in_degrees(), 180)
        self.assertEqual(v.get_length(), 50)

    def test_vector_change_angle_in_radians(self):
        v = Canvas.Vector(30, 30)
        self.assertEqual(v.get_angle_in_degrees(), 45)
        length = v.get_length()
        v.set_angle(math.pi / 2)
        self.assertEqual(v.get_angle_in_degrees(), 90)
        self.assertEqual(v.get_length(), length)
        self.assertEqual(v.get_y(), length)
        self.assertEqual(int(v.get_x()), 0)

    def test_vector_change_angle_in_degrees(self):
        v = Canvas.Vector(45, 45)
        length = v.get_length()
        v.set_angle_in_degrees(135)
        self.assertEqual(v.get_length(), length)
        self.assertEqual(v.get_x(), -45)

if __name__ == "__main__":
    import sys
    sys.path.append(".")
    import canvas as Canvas
    import copy
    unittest.main()
