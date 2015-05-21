
class InvalidParameterValue(Exception):
    pass
    




def parse_params(data):


    try:
        waypoints = data.pop('waypoints')
    except KeyError:
        raise InvalidParameterValue(
            'All routing requests must provide the waypoints parameter')

    if len(waypoints) > 1:
        raise InvalidParameterValue(
            'The waypoints parameter cannot be provided more than once')

    waypoints = waypoints[0]
   
    waypoints = waypoints.split('|')
    waypoints = [x.split(',') for x in waypoints]
    
    waypoints2 = []


    for i, wp in enumerate (waypoints):

        if len(wp) != 2:
            raise InvalidParameterValue(
                'The way point at index {} has too many values'.format(i))

        lat, lon = wp

        try:
            lat = float(lat)
        except ValueError:
            raise InvalidParameterValue(
                'The latitude at index {} cannot be converted to a number'.format(i))

        try:
            lon = float(lon)
        except ValueError:
            raise InvalidParameterValue(
                'The longitude at index {} cannot be converted to a number'.format(i))

        if (lat < -90.) or (90. < lat):
            raise InvalidParameterValue(
                'The latitude at index {} is outside the range [-90, 90]'.format(i))

        if (lon < -180.) or (180. < lon):
            raise InvalidParameterValue(
                'The longitude at index {} is outside the range [-180, 180]'.format(i))

        waypoints2.append((lat, lon))

    preset = None
    if 'preset' in data:
        preset = data.pop('preset')

        if len(preset) > 1:
            raise InvalidParameterValue(
                'The preset parameter cannot be provided more than once')

        
        preset = preset[0].strip()


    multipliers = {}
    for k, v in data.lists():
        if len(v) > 1:
            raise InvalidParameterValue(
                'A multiplier is provided more than once for the {} tag'.format(k))

        v = v[0]

        try:
            v = float(v)
        except ValueError:
            raise InvalidParameterValue(
                'The muliplier for the {} tag cannot be converted to a number'.format(k))


        multipliers[k] = v
        
    if not multipliers:
        multipliers = None

    
    return {'waypoints':waypoints2, 'preset':preset, 'multipliers': multipliers}
