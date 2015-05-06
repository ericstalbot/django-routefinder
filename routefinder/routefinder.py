import networkx
from shapely import geometry


def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
    if distance <= 0.0:
        return [geometry.LineString(), geometry.LineString(line)]
    if distance >= line.length:
        return [geometry.LineString(line), geometry.LineString()]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                geometry.LineString(coords[:i+1]),
                geometry.LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                geometry.LineString(coords[:i] + [(cp.x, cp.y)]),
                geometry.LineString([(cp.x, cp.y)] + coords[i:])]
                
                
def cut_multiple(line, distances):
    
    result = []
    
    leftover = line
    current_distance = 0.
    
    for d in distances:
        
        seg, leftover = cut(leftover, d - current_distance)
        
        result.append(seg)
        
        current_distance += d
        
    result.append(leftover)
    
    return(result)
        
        
        
        
        

                

class MidLinkRouteFinder(object):

    def __init__(self, graph):

        self.graph = graph
        self.digraph = self.buildDiGraph()
        self.addShapes(self.graph)
        self.addShapes(self.digraph)

    def buildDiGraph(self):

        graph = self.graph
        digraph = networkx.MultiDiGraph()

        for nd, data in graph.nodes_iter(data = True):
            digraph.add_node(nd, **data)


        for u, v, k, data in graph.edges_iter(keys = True, data = True):
            coords = data['coords']
            shape_order = tuple(data['shape_order'])
            
            for travel_order in data['travel_order']:

                new_data = data.copy()
                new_data.pop('shape_order')
                new_data.pop('travel_order')

                if travel_order != shape_order:

                    new_data.update({
                        'coords': coords[::-1]
                    })

                
                digraph.add_edge(a, b, k, **data) 

        return digraph
        
        
    def addShapes(self, g):
        #make up front and cache
        for u, v, k, data in g.edges_iter(keys = True, data = True):
            coords = (
                [g.node[u]['coords']] +
                data['coords'] +
                [g.node[v]['coords']]
            )
            shape = geometry.LineString(coords)
            data['shape'] = shape


    def getShapeOrder(self, u, v, k):
        return self.graph[u][v][k]['shape_order'] 


    def insertTempLinks(self, waypoints):
        
        snapped_points = self.getSnappedPoints(waypoints)

        for link, link_points in snapped_points.items():
            self._insert(link, link_points)
            
            
            
    def _insert(self, link, link_points):
        u, v, k = link
        
        link_data = self.graph.get_edge_data(u, v, k).copy()
        link_data.pop('coords')
        shape = link_data.pop('shape')
        
        cut_distances = zip(*link_points)[0]
        segs = cut_multiple(shape, cut_distances)
        
        new_nodes = [networkx.generate_unique_node() for _ in link_points]
        
        nds = [u] + new_nodes + [v]
        
        shape_order = self.getShapeOrder(u, v, k)
        
        for travel_order in self.graph[u][v][k]['travel_order']:
            
            for a, b, seg in zip(nds[:-1], nds[1:], segs):
                    
                if travel_order == shape_order:

                    self.digraph.add_edge(
                        a, b, 
                        attr_dict = link_data,
                        shape = seg,
                        temporary_edge = True
                    )
                    
                else:

                    self.digraph.add_edge(
                        b, a 
                        attr_dict = link_data,
                        shape = geometry.LineString(seg.coords[::-1]),
                        temporary_edge = True
                    )
                    
        for nd in new_nodes:
            self.digraph.node[nd]['temporary_node'] = True
            
        #to do: the new edges must be weighted properly
        #to do: the new edges must be labeled with their waypoint index
        #to do: removing temporary edges and nodes after routing
        #to do: testing
        #to do: documentation
 
    def getSnappedPoints(self, waypoints):
        '''for each point
        
        get nearest link
        
        and distance along link (in shape direction)'''
        
        points = map(geometry.Point, waypoints)
        
        snapped_points = collections.defaultdict(list)

        for i, pnt in enumerate(points):

            nearest_link = self.getNearestLink(pnt)
            dist_along = self.getDistanceAlongLink(pnt, nearest_link)

            u, v, k = nearest_link
            u, v = self.getShapeOrder(u, v, k)
            snapped_points[(u, v, k)].append((dist_along, i))

        for v in snapped_points.values():
            v.sort()

        return snapped_points


    def getNearestLink(self, point):

        edges_iter = self.graph.edges_iter(keys = True, data = True)
        
        u, v, k, data = edges_iter.next()
        min_dist = point.distance(data['shape'])
        min_dist_link = u, v, k

        for u, v, k, data in self.graph.edges_iter(keys = True, data = True):

            dist = point.distance(data['shape'])

            if dist < min_dist:
                min_dist = dist
                min_dist_link = u, v, k

        return min_dist_link

    def getDistanceAlongLink(self, point, link):
        u, v, k = link
        data = self.graph.get_edge_data(u, v, k)
        dist_along = data['shape'].project(point)
        return dist_along

    
        

        

        
        

        
    
