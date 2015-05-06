import unittest
from unittest import TestCase

import networkx


from routefinder import MidLinkRouteFinder

def makeTestData():

    g = networkx.MultiGraph()

    node_coords = [

        (0,0),
        (0,1),
        (1,2),

    ]

    g.add_node(1, coords = (0, 0))
    g.add_node(2, coords = (0, 1))
    g.add_node(3, coords = (1, 2))


    g.add_edge(1, 2,
        coords = [],
        shape_order = (1,2),
        travel_order = [(1,2), (2,1)]
    )

    g.add_edge(2, 3,
        coords = [(0, 2)],
        shape_order = (2,3),
        travel_order = [(2,3), (3,2)]
    )

    return g

    

class TestMidLinkRouteFinder(TestCase):

    def setUp(self):
        self.data = makeTestData()

    def test_routing(self):

        finder = MidLinkRouteFinder(self.data)

        route = finder.findRoute([
            (-0.5, 0.5),
            (-0.5, 1.5)
        ])

        self.assertEqual(
            route.coords
            [(0, 0.5), (0, 1.5)]
            
        )

if __name__ == '__main__':
    unittest.main()
