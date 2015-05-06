import unittest

from unittest import TestCase

from routefinder import MidLinkRouteFinder, RoutingError

import networkx





def getCoords(m, waypoints):
    shp = m.getRoute(waypoints)
    return shp.coords[:]


class TestSingleSimpleLink(TestCase):

    def setUp(self):

        graph = networkx.MultiGraph()
    
        graph.add_node(0, coords = (0,0))
        graph.add_node(1, coords = (1,0))
    
        graph.add_edge(0, 1, coords = [], travel_order = [(0,1)], shape_order = (0,1))

        m = MidLinkRouteFinder(graph)

        self.m = m

    def test_points_on_left(self):

        coords = getCoords(
            self.m,
            [(.25, .25), (.75, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (.75, 0.)]
        )

    def test_points_on_left_and_right(self):

        coords = getCoords(
            self.m,
            [(.25, .25), (.75, -1.0)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (.75, 0.)]
        )

    def test_first_point_off_upstream_end(self):

        coords = getCoords(
            self.m,
            [(-.25, .25), (.75, -1.0)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0., 0.), (.75, 0.)]
        )

    def test_both_points_off_upstream_end(self):

        with self.assertRaises(RoutingError):

            coords = getCoords(
                self.m,
                [(-.25, .25), (-1.0, -1.0)]
            )

    def test_both_points_off_downstream_end(self):

        with self.assertRaises(RoutingError):

            coords = getCoords(
                self.m,
                [(2., .25), (2., -1.0)]
            )
          
    def test_points_in_wrong_order(self):
        with self.assertRaises(RoutingError):

            coords = getCoords(
                self.m,
                [(.75, .25), (.25, .25)]
            )
                
class TestMultipleSimpleLinks(TestCase):

    def setUp(self):
        graph = networkx.MultiGraph()
    
        graph.add_node(0, coords = (0,0))
        graph.add_node(1, coords = (1,0))
        graph.add_node(2, coords = (2,0))
    
        graph.add_edge(0, 1, coords = [], travel_order = [(0,1)], shape_order = (0,1))
        graph.add_edge(1, 2, coords = [], travel_order = [(1,2)], shape_order = (1,2))

        m = MidLinkRouteFinder(graph)

        self.m = m

    def test_points_on_left(self):
        coords = getCoords(
            self.m,
            [(.25, .25), (1.75, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (1.0, 0.0), (1.75, 0.)]
        )

    def test_points_in_wrong_order(self):
        with self.assertRaises(RoutingError):

            coords = getCoords(
                self.m,
                [(1.75, .25), (.25, .25)]
            )

    def test_both_points_off_downstream_end(self):
        with self.assertRaises(RoutingError):

            coords = getCoords(
                self.m,
                [(3.0, .25), (3.0, .25)]
            )

    def test_points_on_single_link(self):
        coords = getCoords(
            self.m,
            [(.25, .25), (0.75, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (0.75, 0.)]
        ) 

    def test_point_on_node(self):
        coords = getCoords(
            self.m,
            [(0., .25), (0.75, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0., 0.), (0.75, 0.)]
        )

class TestLinksWithCoords(TestCase):

    def setUp(self):
        graph = networkx.MultiGraph()
    
        graph.add_node(0, coords = (0,0))
        graph.add_node(1, coords = (1,0))
        graph.add_node(2, coords = (2,0))
    
        graph.add_edge(0, 1, coords = [], travel_order = [(0,1)], shape_order = (0,1))
        graph.add_edge(1, 2, coords = [(1., 1.), (2., 1.)], travel_order = [(1,2)], shape_order = (1,2))

        m = MidLinkRouteFinder(graph)

        self.m = m

    def test_points_on_left(self):
        
        coords = getCoords(
            self.m,
            [(.25, .25), (2.25, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (1., 0.), (1., 1.), (2., 1.), (2., .25)]
        )

    def test_point_on_shape_point(self):
        coords = getCoords(
            self.m,
            [(.25, .25), (.75, 1.25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(.25, 0.), (1., 0.), (1., 1.)]
        )



class TestMixedTravelOrder(TestCase):

    def setUp(self):

        graph = networkx.MultiGraph()

        nodes = [
            (0, 0, 0),
            (1, 0, 1),
            (2, 0, 2),
            (3, 0, 3),
            (4, 1, 1),
            (5, 1, 2)
        ]


        for nd, x, y in nodes:
            graph.add_node(nd, coords = (x,y))

        paths = [
            (0, 1, 2, 3),
            (1, 4, 5, 2), 
        ]

        for path in paths:
            for u, v in zip(path[:-1], path[1:]):
                graph.add_edge(u, v, coords = [],
                    shape_order = (u, v),
                    travel_order = [(u, v)]
                )

        graph[1][2][0]['travel_order'] = [(2, 1)]

        m = MidLinkRouteFinder(graph)

        self.m = m

    def test_one_way_travel_against(self):

        coords = getCoords(
            self.m,
            [(.25, .25), (.25, 2.75)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0, .25), (0, 1), (1, 1), (1, 2), (0, 2), (0, 2.75)]
        )
        
        
    def test_one_way_travel_with(self):

        coords = getCoords(
            self.m,
            [(.25, 1.75), (.25, 2.75)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0, 1.75), (0, 1), (1, 1), (1, 2), (0, 2), (0, 2.75)]
        )
        

class TestTwoWayTravelOrder(TestCase):

    def setUp(self):

        graph = networkx.MultiGraph()

        nodes = [
            (0, 0, 0),
            (1, 0, 1),
            (2, 0, 2),
            (3, 0, 3),
            (4, 1, 1),
            (5, 1, 2)
        ]


        for nd, x, y in nodes:
            graph.add_node(nd, coords = (x,y))

        paths = [
            (0, 1, 2, 3),
            (1, 4, 5, 2), 
        ]

        for path in paths:
            for u, v in zip(path[:-1], path[1:]):
                graph.add_edge(u, v, coords = [],
                    shape_order = (u, v),
                    travel_order = [(u, v), (v, u)]
                )

        graph[1][2][0]['travel_order'] = [(1,2)]

        m = MidLinkRouteFinder(graph)

        self.m = m   

    def test_one_way_travel_with(self):

        coords = getCoords(
            self.m,
            [(.25, .25), (.25, 2.75)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0, .25), (0, 1), (0, 2), (0, 2.75)]
        )
             
    def test_one_way_travel_against(self):

        coords = getCoords(
            self.m,
            [(.25, 2.75), (.25, .25)]
        )
        
        self.assertSequenceEqual(
            coords,
            [(0, 2.75), (0, 2), (1, 2), (1,1), (0, 1), (0, .25)]
        )





#to test
#various travel orders: both, opposite
#various shape orders: forward, reverse
#three or more way points
#test weights, presets, custom weights, providing base_weight
#cutting: one link multiple times
#overlapping routes: doubling back and circling around
#looping edges (back to same node)
#multi edges


if __name__ == '__main__':
    unittest.main()
