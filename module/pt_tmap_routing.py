import numpy as np
import itertools
import requests

from module.helper import *

import warnings 

warnings.filterwarnings('ignore')

def get_res_pt(point) :
    
    url = "https://apis.openapi.sk.com/transit/routes"

    payload = {
        "startX": point[0],
        "startY": point[1],
        "endX": point[2],
        "endY": point[3],
        "lang": 0,
        "format": "json",
        "count": 1
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "appKey": "oMrwPQH9Q010jmOZNIZvT7YmVxHYPGAk5JqRA15d"
    }

    response = requests.post(url, json=payload, headers=headers)

    res = response.json()

    # selected_result = None
    
    # for result in res['metaData']['plan']['itineraries']:
    #     if result['pathType'] == 2 and selected_result is None :
    #         selected_result = result
    #         break
        
    #     elif result['pathType'] == 1 and selected_result is None:
    #         selected_result = result
    #         break
            
    #     elif result['pathType'] == 3 and selected_result is None:
    #         selected_result = result
        
    # return selected_result 
    return res


def extract_duration_distance_pt(result):
       
   duration = result['sectionTime']/60
   distance = result['distance']
    
   return duration, distance

def extract_route(result):
    if result['mode'] == 'SUBWAY' : 
        stationList = result['passStopList']['stationList']
        point = []
        for station in stationList :
            point.append([float(station['lon']),float(station['lat'])])
            
    elif result['mode'] == 'WALK' : 
        walklist = result['passShape']['linestring']
        walklist = walklist.split(' ')
        point = []
        for walk in walklist:
            lon, lat = map(float, walk.split(','))
            point.append([lon, lat])
            
    elif result['mode'] == 'BUS' : 
        buslist = result['passShape']['linestring']
        buslist = buslist.split(' ')
        point = []
        for bus in buslist:
            lon, lat = map(float, bus.split(','))
            point.append([lon, lat])
    return point

def extract_timestamp_pt(route, duration):
    if duration == 0 :
        timestamp = [0.0, 0.0]
    else : 
        rt = np.array(route)
        rt = np.hstack([rt[:-1,:], rt[1:,:]])

        per = calculate_straight_distance(rt[:,1], rt[:,0], rt[:,3], rt[:,2])
        per = per / np.sum(per)

        timestamp = per * duration
        timestamp = np.hstack([np.array([0]),timestamp])
        timestamp = list(itertools.accumulate(timestamp)) 
    
    return timestamp

def pt_routing_machine(O, D) :
    res = get_res_pt([O.x,O.y,D.x,D.y])
    
    datas = []
    
    for i, result in enumerate(res['metaData']['plan']['itineraries'][0]['legs']) :
        if i == 0 or i == len(res['metaData']['plan']['itineraries'][0]['legs']) - 1:
            continue
        duration, distance = extract_duration_distance_pt(result)
        route = extract_route(result)
        timestamp = extract_timestamp_pt(route, duration)
        data = {'mode' : result['mode'], 'route': route, 'timestamp': timestamp, 'duration':duration, 'distance' : distance}
        
        datas.append(data)
        
    return datas

def pt_routing_machine_multiprocess(OD):
   O, D = OD
   result = pt_routing_machine(O, D)
   return result

def pt_routing_machine_multiprocess_all(OD_data):
    results = list(map(pt_routing_machine_multiprocess, OD_data))
    return results