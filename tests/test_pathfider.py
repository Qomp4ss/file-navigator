import unittest
from fpath_fider.pathfinder import PathFinder

class TestFPathFinder(unittest.TestCase):
    
    def test_empty_init(self):
        self.assertIS(PathFinder(), PathFinder)
    