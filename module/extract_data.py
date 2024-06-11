import pandas as pd
import osmnx as ox
import numpy as np

from numpy import random 
import random as rd

from shapely.geometry import Point

from module.kick_tmap_routing import *
from module.pt_tmap_routing import *
from module.helper import *


# 한쌍의 OD 좌표 생성
def point_generator(place=None, count=100, road_type=[2,3], save=False, preview=False):

    G = ox.graph_from_place(place, network_type="drive_service", simplify=False)
    _, edges = ox.graph_to_gdfs(G)

    highway_cat_list = ['motorway', 'motorway_link', 'rest_area', 'services', 'trunk', 'trunk_link']
    mainroad_cat_list = ['primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link']
    minorroad_cat_list = list(set(edges['highway']) - set(highway_cat_list + mainroad_cat_list))
    road_type_dict = {1:highway_cat_list, 2:mainroad_cat_list, 3:minorroad_cat_list}

    target_road = list(itertools.chain(*[road_type_dict[i] for i in road_type]))
    target_edges = edges.loc[[i in target_road for i in edges['highway']]]
    target_edges = target_edges.loc[(target_edges['length'] >= 10)]    
    target_edges = target_edges.reset_index()

    # 좌표 생성
    geometry_inf = []

    for i in random.choice(range(len(target_edges)), size = count*2, replace = True):
        #교차로 중심에 생성되지 않게 고정 미터로 생성이 아닌 해당 링크 길이로 유동적인 미터 생성
        random_num = random.choice([0.1,0.2,0.3,0.4,0.5])
        random_meter = target_edges.iloc[i]["length"] * random_num
        #좌표 생성
        new_node = list(ox.utils_geo.interpolate_points(target_edges.iloc[i]["geometry"], euclid_distance_cal(random_meter)))
        #좌표의 처음과 끝은 노드이기 때문에 제거하고 선택
        del new_node[0], new_node[-1]
        #랜덤으로 선택한 하나의 링크에서 하나의 좌표 선택 
        idx = random.choice(len(new_node), size = 1)
        geometry_loc = new_node[idx[0]]
        geometry_inf.append(geometry_loc)


    geometry_inf = list(map(lambda data: Point(data), geometry_inf))
    geometry_inf = pd.DataFrame(np.array(geometry_inf).reshape(-1, 2), columns=['start_geometry', 'end_geometry'])

    return geometry_inf

def get_OD_data(stops, place, count) : 
    points = point_generator(place=place, count=count, road_type=[2,3])
    
    radius = 0.3  # km
    stops['geometry'] = [Point(lon, lat) for lon, lat in zip(stops['stop_lon'], stops['stop_lat'])]
    # stops['geometry'] = stops.apply(lambda row: Point(row['stop_lon'], row['stop_lat']), axis=1)
    
    for idx, point_row in points.iterrows():
        stops['start_dis'] = calculate_straight_distance(point_row.start_geometry.y, point_row.start_geometry.x, stops.stop_lat, stops.stop_lon)
        stops['end_dis'] = calculate_straight_distance(point_row.end_geometry.y, point_row.end_geometry.x, stops.stop_lat, stops.stop_lon)
        
        stops_start_point = stops[stops['start_dis'] <= radius]
        stops_end_point = stops[stops['end_dis'] <= radius]
        
        if not stops_start_point.empty and not stops_end_point.empty:
            min_start_distance = stops_start_point['start_dis'].max()
            min_end_distance = stops_end_point['end_dis'].max()
            
            min_s_distance_row = stops_start_point[stops_start_point['start_dis'] == min_start_distance]
            min_e_distance_row = stops_end_point[stops_end_point['end_dis'] == min_end_distance]

            if not min_s_distance_row.empty:
                points.at[idx, 'start_stop_geometry'] = min_s_distance_row.iloc[0]['geometry']

            if not min_e_distance_row.empty:
                points.at[idx, 'end_stop_geometry'] = min_e_distance_row.iloc[0]['geometry']
        else:
            # 해당하는 정류장이 없으므로 해당 포인트 제거
            points.drop(idx, inplace=True)
        points.to_csv('./data/points.csv', index=False)
        
    return points

def get_pt_OD_data(OD_data):
    pt_OD_data = []
    for index, row in OD_data.iterrows():
        P_O = row['start_stop_geometry']
        P_D = row['end_stop_geometry']
        pt_OD_data.append([P_O, P_D])

    return pt_OD_data

def get_kick_OD_data(OD_data):
    kick_OO_data = []
    kick_DD_data = []
    for index, row in OD_data.iterrows():
        K_O = row['start_geometry']
        K_D = row['end_geometry']
        kick_OO_data.append([K_O])
        kick_DD_data.append([K_D])

    return kick_OO_data, kick_DD_data

def sample_interval(start, end, count, num_samples):
    interval_size = (end - start) / count
    samples = []
    for i in range(count):
        interval_start = start + interval_size * i
        interval_end = interval_start + interval_size
        samples.extend(rd.sample(range(int(interval_start), int(interval_end)), num_samples))
    return samples

def timestamp_changes(pt_OD, kick_OO, kick_DD, count) :
    
    random_numbers = sample_interval(540, 720, count, 1)
    
    for i in range(len(pt_OD)) :
        for j in range(len(pt_OD[i])-1) :
            pt_OD[i][j+1]['timestamp'] = list(pt_OD[i][j+1]['timestamp'] + pt_OD[i][j]['timestamp'][-1])
        
        kick_OO[i]['timestamp'] = list(np.array(kick_OO[i]['timestamp']) + random_numbers[i])
        for k in range(len(pt_OD[i])) : 
            pt_OD[i][k]['timestamp'] =  list(pt_OD[i][k]['timestamp'] + kick_OO[i]['timestamp'][-1])

        kick_DD[i]['timestamp'] = list(np.array(kick_DD[i]['timestamp']) + pt_OD[i][-1]['timestamp'][-1])
        
        
    return kick_OO, pt_OD, kick_DD

def extract_data(stops, place = '서울', count = 2) :
    OD_data = get_OD_data(stops, place, count)
    pt_OD_data = get_pt_OD_data(OD_data)
    kick_OO_data, kick_DD_data = get_kick_OD_data(OD_data)

    pt_OD = pt_routing_machine_multiprocess_all(pt_OD_data)

    for i in range(len(kick_OO_data)) :
        
        kick_O_end = Point(pt_OD[i][0]['route'][0])
        kick_D_start = Point(pt_OD[i][-1]['route'][-1])
        kick_OO_data[i].insert(1, kick_O_end)
        kick_DD_data[i].insert(0, kick_D_start)
        
    kick_OO = kickboard_routing_machine_multiprocess_all(kick_OO_data)
    kick_DD = kickboard_routing_machine_multiprocess_all(kick_DD_data)
    
    kick_OO, pt_OD, kick_DD = timestamp_changes(pt_OD, kick_OO, kick_DD, count) 
    
    data = []
    for list in pt_OD:
        for dict in list :
            data.append(dict)

    pt_OD = data
    
    return kick_OO, pt_OD, kick_DD




