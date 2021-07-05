import unittest
from get_feature_nvdi import get_geo_feature

class TestGetGeoFeature(unittest.TestCase):
    def test_input_type(self):
        self.assertRaises(TypeError, get_geo_feature, True)