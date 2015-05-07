
from django.http import HttpResponse, JsonResponse

from route_finder_instance import crs, units2miles, rf
import pyproj
p = pyproj.Proj(crs)

from shapely import geometry


def process_params(data):

    waypoints = data['waypoints']
    waypoints = waypoints.split(',')
    waypoints = [x.strip() for x in waypoints]
    
    lats, lons = [], []
    
    while waypoints:
        
        lats.append(float(waypoints.pop(0)))
        lons.append(float(waypoints.pop(0)))
        
    assert len(lats) == len(lons)
    
    return {'waypoints':zip(lats, lons)}
        
    

def find(request):


    data = request.GET
    
    #catch all block
    #we never want to return anything but a 200
    #we just want to change the status code and message that is
    #returned
    #and maybe return warnings too?
    try:
        #params block
        try:
            args = process_params(data)
        except: #add specific error type here
            pass #re-raise here
        
            
        #routefinder block
        try:
            result = rf.getRoute(**args)
        except routefinder.NoPath as e:
            pass
        except routefinder.InvalidInput as e:
            pass
            
            
    except Exception as e:
        pass
    
    
    return JsonResponse({'coords': result.coords})

    
#to do
#weights - presets and multipliers
#projection (both ways)
#switch back to y,x order
#add detail to response object (not just shape)
#add status to response object
#add error handling (including expected errors, unexpected errors)
#possible statuses
#   no routing attempted
#       less than two way points
#       collapse to less than two points
#       
#
#       invalid input
#       
#           not right parameters
#           etc
#   routing attempted, but no route found
#   
#   other errors
#       catch all - should have these infrequently




#




    
