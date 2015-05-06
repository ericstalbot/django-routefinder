from django.test import TestCase
from django.core.urlresolvers import reverse

import json
import networkx


def makeTestData():

    g = networkx.DiGraph()
    
    g.add_node(
        1,
        coords = [-80., 30.]
    )
    
    g.add_node(
        2,
        coords = [-80., 30.001]
    )
    
    g.add_node(
        3,
        coords = [-79.999, 30.002]
        
    )
    
    g.add_edge(
        1, 2, 
        coords = [],
        tags = ['gravel','class3']
    )
    
    g.add_edge(
        2, 1, 
        coords = [],
        tags = ['gravel', 'class3']
    )
    
    g.add_edge(
        2, 3,
        coords = [(-80., 30.002)],
        tags = ['paved', 'state_highway']
    )

    g.add_edge(
        3, 2,
        coords = [(-80., 30.002)],
        tags = ['paved', 'state_highway']
    )
    
    return g




class RouterFinderTests(TestCase):

    def setUp(self):
        
        self.network = makeTestData()
        
    def test_basic_routing(self):
        
        rf = RouteFinder(self.network)
        
        route = rf.getRoute(
            [
                (-80.0001, 30.0005), 
                (-80.0001, 30.0015)
            ],
            {'paved':1.2}
        )
        
        self.assertEqual(
            route,
            [   
                (-80.0000, 30.0005), 
                (-80.0000, 30.0015)
            ]
        )
        

