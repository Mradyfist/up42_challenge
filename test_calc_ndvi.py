import unittest
from get_feature_nvdi import calc_ndvi

class TestCalcNDVI(unittest.TestCase):

    def test_basic(self):
        self.assertAlmostEqual(calc_ndvi(8, 5, 0), 0.23076923076923078)
