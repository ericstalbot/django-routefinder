

from route_finder_instance import crs, units2miles, rf
import pyproj
p = pyproj.Proj(crs)



def find(request):

    if request.method != 'GET':
        return #need to return a proper response

    data = request.GET

    try:
        waypoints = request['waypoints']
    except KeyError as e:
        return

    try:
        preset = request['preset']
    except KeyError as e:
        

    


    
