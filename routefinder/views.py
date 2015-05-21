
from django.http import HttpResponse, JsonResponse
import pyproj

from parse_params import parse_params, InvalidParameterValue

from route_finder_instance import crs, rf
from routefinder import InvalidInput




        

p_wgs84 = pyproj.Proj(init='epsg:4326', no_defs=True)
p_rf  = pyproj.Proj(**crs)

def latlon2xy(waypoints):
    lats, lons = zip(*waypoints)
    x, y = pyproj.transform(p_wgs84, p_rf, lons, lats)
    return zip(x,y)

def xy2latlon(coords):
    x, y = zip(*coords)
    lons, lats = pyproj.transform(p_rf, p_wgs84, x, y)
    return zip(lats, lons)



def find(request):


    status = 'ok'

    data = request.GET.copy()
    
    try:
        args = parse_params(data)
        
        waypoints = args['waypoints']
        args.update({'waypoints': latlon2xy(waypoints)})

        result = rf.getRoute(**args)

    except (InvalidInput, InvalidParameterValue) as e:
        status = 'invalid_request'

    except routefinder.NoPath as e:
        status = 'no_path'

    if status != 'ok':
        return JsonResponse({'status': status, 'message': e.message})
                
    #to do: limit the number of digits on the 
    #returned coords
    response = {
        'status': status,
        'coords': xy2latlon(result.coords)
    }
    return JsonResponse(response)
    
