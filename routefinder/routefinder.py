
import networkx

from shapely import geometry

def cut(line, distance):
    # Cuts a line in two at a distance from its starting point
##    if distance <= 0.0:
##        return [geometry.LineString(), geometry.LineString(line)]
##    if distance >= line.length:
##        return [geometry.LineString(line), geometry.LineString()]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(geometry.Point(p))
        if pd == distance:
            return [
                geometry.LineString(coords[:i+1]),
                geometry.LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                geometry.LineString(coords[:i] + [(cp.x, cp.y)]),
                geometry.LineString([(cp.x, cp.y)] + coords[i:])]


class RoutingError(Exception):
    pass
    
class InvalidInput(RoutingError):
    pass
    
class NoPath(RoutingError):
    pass

class RouteFinderResponse(object):
    pass
    
    

class MidLinkRouteFinder(object):

    def __init__(self, graph, weight_presets = None, has_base_weights = False):
        
    
        self.graph = graph
        if weight_presets is None:
            weight_presets = {}
        self.weight_presets = weight_presets
        
        self.addShapes()

        if not has_base_weights:
            self.setBaseWeights()

        self.setPresetWeights()
        
        self.digraph = networkx.MultiDiGraph()
        self.populateDiGraph()

    def getShapeOrder(self, u, v, k):
        return tuple(self.graph[u][v][k]['shape_order'])

    def addShapes(self):
        graph = self.graph
        for u, v, k, data in graph.edges_iter(keys = True, data = True):
            u, v = self.getShapeOrder(u, v, k)
            coords = (
                [graph.node[u]['coords']] +
                data.pop('coords') +
                [graph.node[v]['coords']]
            )
            shape = geometry.LineString(coords)
            data['shape'] = shape


    def setBaseWeights(self):
        for u, v, k, data in self.graph.edges_iter(keys = True, data = True):
            data['base_weight'] = data['shape'].length
        
        
    def setPresetWeights(self):

        for weight_name, multipliers in self.weight_presets.items():
            self.weightGraph(multipliers, weight_name)


    def weightGraph(self, multipliers, weight_name):
        graph = self.graph
        for u, v, k, data in graph.edges_iter(keys = True, data = True):

            m = 1.0
            link_tags = data.get('tags', {})
            base_weight = data['base_weight']

            for tag, mul in multipliers.items():
                if tag in link_tags:
                    m *= mul

            data[weight_name] = base_weight * m


    def populateDiGraph(self):
        graph = self.graph
        digraph = self.digraph
        
        for u, v, k in graph.edges_iter(keys = True):
            self.copyEdgeToDiGraph(u, v, k)
                
    def copyEdgeToDiGraph(self, u, v, k):
        graph = self.graph
        digraph = self.digraph

        data = graph.get_edge_data(u, v, k)

        weights = {}
        weight_names = (['base_weight', 'custom_weight'] +
                        self.weight_presets.keys())
        for wn in weight_names:
            if wn in data:
                weights[wn] = data[wn]

        
        for (a, b) in data['travel_order']:
            
            digraph.add_edge(a, b, key = k, **weights)
    
    def insertNode(self, point):
        graph = self.graph

        point = geometry.Point(point)
        target_link = self.getNearestLink(point)


        dist_along = self.getDistanceAlongLink(point, target_link)
        
        
        link_data = graph.get_edge_data(*target_link).copy()
        travel_order = link_data.pop('travel_order')
        shape_order = link_data.pop('shape_order')
        
        shp = link_data.pop('shape')
        shp_len = shp.length

        if dist_along <= 0.0:
            return shape_order[0], False
        if dist_along >= shp_len:
            return shape_order[1], False



        seg0, seg1 = cut(shp, dist_along)
       
        new_node = networkx.utils.generate_unique_node()
        u, v, k = target_link
        u, v = shape_order
        
        def replace(l, old):
            l = list(l)
            l[l.index(old)] = new_node
            return tuple(l)
        
        def new_travel_order(dropped_node):
            return map(lambda pair: replace(pair, dropped_node), travel_order)
            
        def new_shape_order(dropped_node):
            return replace(shape_order, dropped_node)
       
        #we dn't really need to copy *all* the weights,
        #just the one that is being used for routing
        def new_weights(new_len):
            weight_names = (
                ['base_weight', 'custom_weight'] +
                self.weight_presets.keys()
            )
            ratio = new_len / shp_len
            result = {}
            for wn in weight_names:
                if wn in link_data:
                    result[wn] = link_data[wn] * ratio
            return result

        graph.add_edge(
            u, new_node, key = k,
            attr_dict = link_data,
            shape = seg0,
            shape_order = new_shape_order(v),
            travel_order = new_travel_order(v),
            **new_weights(seg0.length)
        )
        
        graph.add_edge(
            new_node, v, key = k,
            attr_dict = link_data,
            shape = seg1,
            shape_order = new_shape_order(u),
            travel_order = new_travel_order(u) ,
            **new_weights(seg1.length)
        )
        
        graph.remove_edge(u, v, k)
        
        self.copyEdgeToDiGraph(u, new_node, k)
        self.copyEdgeToDiGraph(new_node, v, k)
        
        for a, b in travel_order:
            self.digraph.remove_edge(a, b, k)

        return new_node, True

    def getNearestLink(self, point):

        graph = self.graph
    
        edges_iter = graph.edges_iter(keys = True, data = True)
        
        u, v, k, data = edges_iter.next()
        min_dist = point.distance(data['shape'])
        min_dist_link = u, v, k


        for u, v, k, data in edges_iter:

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
            

    def _getRoute(self, waypoints, multipliers = None, preset = None):

        if len(waypoints) < 2:
            raise InvalidInput('Must provide at least 2 waypoints')

        if (multipliers is not None) and (preset is not None):
            raise InvalidInput('multipliers and preset cannot both be specified')
        
        if multipliers is not None:
            weight_name = 'custom_weight'
            self.weightGraph(multipliers, weight_name)

        elif preset is not None:
            if preset not in self.weight_presents:
                raise InvalidInput('the value for preset is not one of the options')
            weight_name = preset

        else:
            weight_name = 'base_weight'

        
        waypoint_nodes = []
        nodes_to_remove = []
        for waypoint in waypoints:
            nd, is_new = self.insertNode(waypoint)
            waypoint_nodes.append(nd)
            if is_new:
                nodes_to_remove.append(nd)


        if len(set(waypoint_nodes)) < 2:
            raise InvalidInput('the waypoints collapse to fewer than 2 nodes')

        nodes, keys = [], []

        for nd0, nd1 in zip(waypoint_nodes[:-1], waypoint_nodes[1:]):
            nds, kys = self.getPath(nd0, nd1, weight_name)
            nodes.extend(nds[:-1])
            keys.extend(kys)

        nodes.append(nds[-1])

        return nodes, keys
    
    def getRoute(self, waypoints, multipliers = None, preset = None):
        
        nodes, keys = self._getRoute(waypoints, multipliers, preset)
        
        result = RouteFinderResponse()
        
        result.coords = self.getRouteCoords(nodes, keys)
        
        return result

        
            

    def getPath(self, nd0, nd1, weight_name):
        
        try:
            _, nodes = networkx.bidirectional_dijkstra(
                self.digraph,
                nd0, nd1,
                weight_name
            )
        except networkx.NetworkXNoPath:
            raise NoPath('no path found between the points')


        def getKey(u, v):
            keys = []
            for k in self.digraph[u][v]:
                weight = self.digraph[u][v][k][weight_name]
                keys.append((weight, k))
            keys.sort()
            return keys[0][1]

        keys = []
        for a, b in zip(nodes[:-1], nodes[1:]):
            k = getKey(a,b)
            keys.append(k)

        return nodes, keys

    def getLinkCoords(self, link):
        u, v, k = link

        shape_order = self.getShapeOrder(u, v, k)

        shp = self.graph[u][v][k]['shape']

        if (u, v) == shape_order:
            return shp.coords[:]

        else:
            return shp.coords[::-1]


    def getRouteCoords(self, nodes, keys):


        links = iter(zip(nodes[:-1], nodes[1:], keys))


        result = []

        link = links.next()

        result.extend(self.getLinkCoords(link))

        for link in links:
            result.extend(self.getLinkCoords(link))

        return result




#to do: joining links back together              
        
        

    
    
    
