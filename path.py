from pyproj import Proj, transform
from bs4 import BeautifulSoup
from utils import *
import math
import numpy as np
import airsim

# 读取KML文件
def readkml(path):
    '''

    :param path: 路径文件路径
    :return: 解析的KML
    '''

    with open(path, 'r') as f:
        kml_doc = f.read()

    # 解析KML文件
    soup = BeautifulSoup(kml_doc, 'lxml-xml')

    return soup

# 提取kml文件信息
def extracting(soup, args):
    '''

    :param soup: 解析的KML
    :param args: 参数
    :return: GPS坐标列表
    '''
    placemarks = soup.find_all('Placemark')

    pos = {}
    # 循环遍历每个Placemark元素
    for placemark in placemarks:
        # 提取名称和坐标数据
        name = placemark.find('name').text

        coordinate = {}

        if placemark.find('coordinates'):
            coordinates = placemark.find('coordinates').text
            # 将坐标数据拆分成经度、纬度、高度三个值
            longitude, latitude, altitude = coordinates.split(',')
            coordinate['longitude'] = float(longitude)
            coordinate['latitude'] = float(latitude)
            coordinate['altitude'] = float(altitude)

        if placemark.find('mis:heading'):
            yal = placemark.find('mis:heading').text
            args.target_yal = float(yal)

        if placemark.find('mis:gimbalPitch'):
            gimbalPitch = placemark.find('mis:gimbalPitch').text
            args.target_pitch = float(gimbalPitch)

        pos[name] = coordinate

    return pos

# 将GPS坐标经纬度转换为局部坐标XY
def GPSToXY(lat, lon, ref_lat, ref_lon):
    '''

    :param lat: 需要被转换的纬度
    :param lon: 需要被转换的经度
    :param ref_lat: 参照物纬度（起飞点的纬度）
    :param ref_lon: 参照物经度（起飞点的经度）
    :return: 转换后的局部坐标系x, y
    '''

    CONSTANTS_RADIUS_OF_EARTH = 6371000.  # meters (m)

    # input GPS and Reference GPS in degrees
    # output XY in meters (m) X:North Y:East
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    cos_d_lon = math.cos(lon_rad - ref_lon_rad)

    arg = np.clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0)
    c = math.acos(arg)

    k = 1.0
    if abs(c) > 0:
        k = (c / math.sin(c))

    x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH)
    y = float(k * cos_lat * math.sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH)

    return x, y

# 将GPS坐标转化为XYZ坐标
def GPSToPOS(pos, args):
    '''

    :param pos: GPS坐标系列表
    :param args: 参数
    :return: xyz坐标列表
    '''

    positions = []
    for Waypoint in pos:
        if Waypoint == 'Wayline':
            continue

        # 定义目标位置的经纬度坐标
        target_lat = pos[Waypoint]['latitude']
        target_lon = pos[Waypoint]['longitude']
        x, y = GPSToXY(target_lat, target_lon, args.init_place[0], args.init_place[1])
        z = pos[Waypoint]['altitude']
        positions.append([y, -x, z])

    return positions


# 将路径进行横向平移
def horizontal_move_path(paths, k, adjust_value=15):
    '''

    :param paths: 路径数据
    :param k: 路径的斜率
    :param adjust_value: 横向平移值
    :return: 调整后的路径
    '''
    i = 0
    for path in paths:
        x, y = path[0], path[1]
        x = x + math.cos(math.atan(k)) * adjust_value
        y = y + math.sin(math.atan(k)) * adjust_value
        paths[i][0] = x
        paths[i][1] = y
        i += 1

    return paths


# 将路径进行纵向平移
def vertical_move_path(paths, k, adjust_dis):
    '''

    :param paths: 路径数据
    :param k: 路径的斜率
    :param adjust_dis: 纵向平移值
    :return:
    '''
    delta_x, delta_y = adjust_distance(adjust_dis, k)
    print(delta_x, delta_y)
    paths_ = []
    for path in paths:
        x, y, z = path[0], path[1], path[2]
        x = x + delta_x
        y = y + delta_y
        paths_.append([x, y, z])

    return paths_

# 初始化路径
def init_path(path, args):
    '''

    :param path: 路径文件路径
    :param args: 参数
    :return: 无人机的飞行路径
    '''
    # 读取路径文件
    soup = readkml(path)
    # 提取文件中有关飞行器的信息
    pos = extracting(soup, args)
    # 将GPS坐标转化为局部坐标xy
    paths = GPSToPOS(pos, args)
    # 获取飞行路径斜率
    args.k = get_path_k(paths[0][0], paths[12][0], paths[0][1], paths[12][1])
    # 平移路径
    paths = horizontal_move_path(paths, args.k)

    return paths

# 创建路径
def create_path(paths):
    '''

    :param paths:路径数据
    :return: AirSim可识别的路径格式
    '''

    waypoints = []
    for path in paths:
        # 定义路径点
        waypoints.append(airsim.Vector3r(path[0], path[1], -path[2]))

    # 将路径点转换为AirSim可识别的格式
    airsim_path = [(waypoint.x_val, waypoint.y_val, waypoint.z_val) for waypoint in waypoints]

    return airsim_path
