

from . import routing_profiles



    
        
    
        
    
        

    










class RouteFinder(object):

    def __init__(self, network, routing_profiles):
    
        self.graph = network
        self.routing_profiles = routing_profiles    
    
    def getDataOrder(self, u, v, k):
        '''order uv in data order'''
        return tuple(self.graph[u][v][k]['data_order'])
    
    def getTravelOrder(self, u, v, k):
        '''get travel order
        returns either one or two orderings of u, v
        
        '''
        return map(tuple, self.graph[u][v][k]['travel_order'])
        
    

    def getSnapPositions(self, points):
        '''Returns a dict
        
        keys are links identified by u, v, k
        
        values are lists of (dist, i, pnt)
        
        where dist is the distance along the link
        i is the index of the point in the points parameter
        pnt is the point geometry
        
        the u, v order in the keys is always the data order
        
        the dist is always the distance in the data order
        
        the ordering of the values is according to distance along link
        
        '''

        result = collections.DefaultDict(list)
        
        points = map(geometry.Point, points)
        
        for i, point in enumerate(points):
        
            u, v, k = self.getNearestLink(point)
            dist_along = self.getDistAlongLink(point, u, v, k)
        
            u, v = gelf.getDataOrder(u, v, k)
            
            result[(u, v, k)].append((dist_along, i, point))
            
        for v in result.values():
            v.sort()
            
        return result
   
    
    def getNearestLink(self, point):
        '''nearest link on graph
        
        ordering of u, v is not defined'''
        
        edges_iter = self.graph.edges_iter(data = True)
        
        u, v, k, data = edges_iter.next()
        min_dist_edge = u, v, k
        min_dist = data['shape'].distance(point)
        
        for u, v, k, data in edges_iter:
            
            dist = data['shape'].distance(point)
            
            if dist < min_dist:
                
                min_dist_edge = u, v, k
                min_dist = dist
        
        return min_dist_edge
    
    
    
    def getDistAlongLink(self, point, u, v, k):
        #dist along is in direction of data
        linestring = self.graph[u][v][k]['shape']
        return linestring.project(point)
    

    

    
        
    
    
    
    
    
    
    
    
    
    
    
        
    
    
        