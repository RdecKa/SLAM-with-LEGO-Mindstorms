import unittest

import numpy as np

import slam.common.datapoint as datapoint
import slam.common.geometry as geometry
import slam.display.storage as storage
from slam.common.enums import Existence

raw_scatter_data = np.array([
    [5, 7, 0.1, 0.5, 0.6, 0.3],
    [-1, 8, 0.9, 0.1, 0.1, 0.3],
    [-5, -50, 0.9, 0.1, 0, 0.5],
])


def arrays_almost_equal(a1: np.ndarray, a2: np.ndarray):
    if a1.shape != a2.shape:
        return False
    return np.all(np.isclose(a1, a2))


class TestScatterStorage(unittest.TestCase):
    def setUp(self):
        self.storage = storage.ScatterStorage()

    def add_raw_data(self, existence: Existence = Existence.PERMANENT):
        for row in raw_scatter_data:
            data = datapoint.DataPoint(*row[0:2], color=row[2:6],
                                       existence=existence)
            self.storage.add_data(data)

    def test_add_data(self):
        self.add_raw_data()
        stored_permanent_data = self.storage.data[Existence.PERMANENT].data
        self.assertTrue(
            arrays_almost_equal(stored_permanent_data, raw_scatter_data))

        stored_temporary_data = self.storage.data[Existence.TEMPORARY].data
        self.assertTrue(
            arrays_almost_equal(stored_temporary_data, np.empty([0, 6])))

    def test_get_data(self):
        self.add_raw_data()
        x_data, y_data, c_data = self.storage.get_data()
        self.assertTrue(arrays_almost_equal(x_data, raw_scatter_data[:, 0]))
        self.assertTrue(arrays_almost_equal(y_data, raw_scatter_data[:, 1]))
        self.assertTrue(arrays_almost_equal(c_data, raw_scatter_data[:, 2:6]))

    def test_delete_temporary_data(self):
        self.add_raw_data(existence=Existence.TEMPORARY)
        self.storage.delete_temporary_data()
        stored_temporary_data = self.storage.data[Existence.TEMPORARY].data
        self.assertTrue(
            arrays_almost_equal(stored_temporary_data, np.empty([0, 6])))


raw_heatmap_data = np.array([
    [10, 9],
    [-5, 0],
    [-1, 8],
])

heatmap_origin = geometry.Point(-5, -5)

heatmap_expected = np.array([
    [-5, -5, 10],
    [-4, -5, 9],
    [-5, -4, -5],
    [-4, -4, 0],
    [-5, -3, -1],
    [-4, -3, 8],
])


class TestHeatmapStorage(unittest.TestCase):
    def setUp(self):
        self.storage = storage.HeatmapStorage()

    def add_raw_data(self):
        data = datapoint.Prediction(*heatmap_origin, raw_heatmap_data)
        self.storage.set_data(data)

    def test_set_data(self):
        self.add_raw_data()
        self.assertTrue(
            arrays_almost_equal(self.storage.data, heatmap_expected))

    def test_get_data(self):
        self.add_raw_data()
        x, y, c = self.storage.get_data()
        self.assertTrue(arrays_almost_equal(heatmap_expected[:, 0], x))
        self.assertTrue(arrays_almost_equal(heatmap_expected[:, 1], y))
        self.assertTrue(arrays_almost_equal(heatmap_expected[:, 2], c))


raw_path_data = np.array([
    [5, 6],
    [9, -8],
    [-5, -8],
])


class TestPathStorage(unittest.TestCase):
    def setUp(self):
        self.storage = storage.PathStorage()

    def add_raw_data(self, path_id: int,
                     existence: Existence = Existence.PERMANENT):
        for row in raw_path_data:
            data = datapoint.DataPoint(*row[0:2], path_id=path_id,
                                       existence=existence)
            self.storage.add_data(data)

    def test_add_data(self):
        self.add_raw_data(1)
        self.add_raw_data(2)
        self.assertTrue(
            arrays_almost_equal(self.storage.data[1].data, raw_path_data))
        self.assertTrue(
            arrays_almost_equal(self.storage.data[2].data, raw_path_data))

        self.add_raw_data(2)
        stacked = np.vstack((raw_path_data, raw_path_data))
        self.assertTrue(
            arrays_almost_equal(self.storage.data[2].data, stacked))

    def test_get_data(self):
        self.add_raw_data(1)
        self.add_raw_data(100)
        data = self.storage.get_data()
        self.assertTrue(arrays_almost_equal(data[1].data, raw_path_data))
        self.assertTrue(arrays_almost_equal(data[100].data, raw_path_data))

    def test_delete_temporary_data(self):
        self.add_raw_data(13, Existence.TEMPORARY)
        self.add_raw_data(42, Existence.PERMANENT)
        self.storage.delete_temporary_data()
        data = self.storage.get_data()
        self.assertTrue(arrays_almost_equal(data[13].data, np.empty([0, 2])))
        self.assertTrue(arrays_almost_equal(data[42].data, raw_path_data))
