import numpy as np
import itertools
import requests

from module.helper import *

import warnings

warnings.filterwarnings('ignore')

def get_kickres(point) :
    
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&callback=function"

    payload = {
        "startX": point[0],
        "startY": point[1],
        "angle": 20,
        "speed": 30,
        "endX": point[2],
        "endY": point[3],
        "reqCoordType": "WGS84GEO",
        "startName": [point[0],point[1]],
        "endName": [point[2],point[3]],
        "searchOkickboardion": "0",
        "resCoordType": "WGS84GEO",
        "sort": "index"
    }
    headers = {
        "accekickboard": "application/json",
        "content-type": "application/json",
        "appKey": "oMrwPQH9Q010jmOZNIZvT7YmVxHYPGAk5JqRA15d"
    }

    response = requests.post(url, json=payload, headers=headers)
    res = response.json()
    return res

def extract_duration_distance_kick(res):
   
   duration = res['features'][0]['properties']['totalTime']/60
   distance = res['features'][0]['properties']['totalDistance']
   
   return duration, distance

def extract_route_kick(res):
    
    point =  []
    for i, result in enumerate(res['features']) :
        if result['geometry']['type'] == 'Point' :
            continue
            
        else :
            routes = result['geometry']['coordinates']
            for route in routes :
                point.append(route)   
   
    return point
 
def extract_timestamp_kick(route, duration):
    
    rt = np.array(route)
    rt = np.hstack([rt[:-1,:], rt[1:,:]])

    per = calculate_straight_distance(rt[:,1], rt[:,0], rt[:,3], rt[:,2])
    per = per / np.sum(per)

    timestamp = per * duration
    timestamp = np.hstack([np.array([0]),timestamp])
    timestamp = list(itertools.accumulate(timestamp)) 
    
    return timestamp

def kickboard_routing_machine(O,D) :
    
    res = get_kickres([O.x, O.y, D.x, D.y])
    duration, distance = extract_duration_distance_kick(res)
    route = extract_route_kick(res)
    timestamp = extract_timestamp_kick(route, duration)
    
    data = {'mode' : 'KICKBOARD', 'route': route, 'timestamp': timestamp, 'duration': duration, 'distance' : distance}
    
    return data 

def kickboard_routing_machine_multiprocess(OD):
   O, D = OD
   result = kickboard_routing_machine(O, D)
   return result

def kickboard_routing_machine_multiprocess_all(OD_data):
    results = list(map(kickboard_routing_machine_multiprocess, OD_data))
    return results   
