import cv2
import math
import time
import airsim
from lidar import *
from plot import *
from pid import PID


cameraTypeMap = {
    "depth": airsim.ImageType.DepthVis,  # 黑白景深图像
    "segmentation": airsim.ImageType.Segmentation,  # 彩色目标分割图像
    "seg": airsim.ImageType.Segmentation,  # 彩色目标分割图像
    "scene": airsim.ImageType.Scene,  # 正常图像
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
}


# 获取当前无人机信息
def updata_uavdata(client, vehicle_name=''):
    '''

    :param client: 无人机客户端
    :param vehicle_name: 无人机名称
    :return: 无人机得到相关信息（msg）
    '''

    # 获取无人飞机的所有数据
    Flystate = client.getMultirotorState(vehicle_name=vehicle_name)

    # 从所有数据扣出 position坐标  北偏地坐标系
    position = Flystate.kinematics_estimated.position
    gps_data = Flystate.gps_location
    imu_data = Flystate.kinematics_estimated.orientation

    msgs = {}
    msg = {}
    msg['X'] = position.x_val
    msg['Y'] = position.y_val
    msg['Z'] = position.z_val
    msg['altitude'] = gps_data.altitude
    msg['latitude'] = gps_data.latitude
    msg['longitude'] = gps_data.longitude
    pitch, roll, yaw = airsim.to_eularian_angles(imu_data)
    msg['yaw'] = math.degrees(yaw)
    msg['pitch'] = math.degrees(pitch)
    msg['roll'] = math.degrees(roll)
    if vehicle_name == 'Drone1':
        msgs[vehicle_name] = msg

    elif vehicle_name == 'Drone2':
        msgs[vehicle_name] = msg
    return msgs


def saveimg(client, args):
    '''

    :param client: 无人机客户端
    :param args: 参数
    '''

    temp_image = client.simGetImage('0', cameraTypeMap[args.cameraType])

    # 将图像进行解码，变成像素值为0-255的范围，保存路径自行修改
    image = cv2.imdecode(airsim.string_to_uint8_array(temp_image), cv2.IMREAD_COLOR)
    if not os.path.exists('./data/photo/'):
        os.makedirs('./data/photo/')
    cv2.imwrite('data/photo/visual-{}.png'.format(time.time()), image)


# 将无人机旋转至指定偏航角
def rotateBytargetYaw(client, targetYam, args, visual=False, vehicle_name=''):
    '''

    :param client: 无人机客户端
    :param targetYam: 目标偏航角
    :param args: 参数
    :param visual: 是否可视化
    :param vehicle_name: 无人机名称
    '''

    times = []
    yaws = []
    error = 1
    t = 0
    while True:
        msgs = updata_uavdata(client, vehicle_name=vehicle_name)
        deviate_angle = targetYam - msgs[vehicle_name]['yaw']
        times.append(t)
        yaws.append(msgs[vehicle_name]['yaw'])
        if abs(deviate_angle) < error:
            break
        client.rotateByYawRateAsync(deviate_angle * args.rate, 1.0, vehicle_name=vehicle_name)
        time.sleep(0.5)
        t += 0.5

    if visual:
        plot_yaw(times, yaws, targetYam, error)


# 利用pid算法将无人机旋转至指定偏航角
def rotateBytargetYaw_pid(client, targetYam, args, visual=False, vehicle_name=''):
    '''

    :param client: 无人机客户端
    :param targetYam: 目标偏航角
    :param args: 参数
    :param visual: 是否可视化
    :param vehicle_name: 无人机名称
    '''

    pid = PID(0.15, 0.15, 0.5)
    times = []
    yaws = []
    error = 1.0
    t = 0
    while True:
        msgs = updata_uavdata(client, vehicle_name=vehicle_name)
        deviate_angle = targetYam - msgs[vehicle_name]['yaw']
        times.append(t)
        yaws.append(msgs[vehicle_name]['yaw'])
        if abs(deviate_angle) < error:
            break
        rotate_angle = pid.update(deviate_angle, 0.5)
        client.rotateByYawRateAsync(rotate_angle, 1.0, vehicle_name=vehicle_name)
        time.sleep(0.5)
        t += 0.5

    if visual:
        plot_yaw(times, yaws, targetYam, error)


# 在无人机当前位置和目标位置之间插入更多的位置点
def insert_points(client, point, num, vehicle_name=''):
    '''

    :param client: 无人机客户端
    :param point: 目标点
    :param num: 插入点的数量
    :param vehicle_name: 无人机名称
    :return: 位置点列表
    '''

    msgs = updata_uavdata(client, vehicle_name=vehicle_name)
    delta_x = (point[0] - msgs[vehicle_name]['X']) / num
    delta_y = (point[1] - msgs[vehicle_name]['Y']) / num
    delta_z = (point[2] - msgs[vehicle_name]['Z']) / num
    x, y, z = msgs[vehicle_name]['X'], msgs[vehicle_name]['Y'], msgs[vehicle_name]['Z']

    points = []
    for i in range(num):
        x += delta_x
        y += delta_y
        z += delta_z
        points.append(airsim.Vector3r(x, y, -z))

    return points


# 获取路径斜率
def get_path_k(x1, x2, y1, y2):
    '''

    :param x1:
    :param x2:
    :param y1:
    :param y2:
    :return: 斜率k
    '''
    k = (y2 -y1) / (x2 - x1)
    return k

# 获取路径的xy的平移值
def adjust_distance(div_distance, k):
    '''

    :param div_distance: 当前距离与目标距离的差
    :param k: 斜率
    :return: x, y的偏移量
    '''

    angle = math.atan(k) + math.pi/2

    delta_x = math.cos(angle) * div_distance
    delta_y = math.sin(angle) * div_distance

    return delta_x, delta_y


