from routefinder import MidLinkRouteFinder
from weight_presets import weight_presets


import networkx
import fiona.crs

def get_graph():
    graph = networkx.MultiGraph()
    
    graph.add_node(0, coords = (0, 0))
    graph.add_node(1, coords = (1, 0))
    
    graph.add_edge(0, 1, coords = [],
                    shape_order = (0, 1),
                    travel_order = [(0, 1)])
                    
    return graph


multigraph = get_graph()

crs = fiona.crs.from_epsg(4326) 
units2miles = None


rf = MidLinkRouteFinder(multigraph, weight_presets)
