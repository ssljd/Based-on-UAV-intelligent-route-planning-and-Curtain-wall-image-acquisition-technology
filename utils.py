import cv2
import os
import math
import time
import airsim
import numpy as np
from lidar import *
import pygame
import matplotlib
import matplotlib.pyplot as plt

colors = []
for name, hex in matplotlib.colors.cnames.items():
    colors.append(name)

# 更新当前无人机信息
def updata_uavdata(client, vehicle_name=''):
    '''

    :param client:
    :param args:
    :return:
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

def saveimg(client, cameraTypeMap, args):
    '''

    :param client:
    :param cameraTypeMap:
    :param args:
    :return:
    '''

    temp_image = client.simGetImage('0', cameraTypeMap[args.cameraType])

    # 将图像进行解码，变成像素值为0-255的范围，保存路径自行修改
    image = cv2.imdecode(airsim.string_to_uint8_array(temp_image), cv2.IMREAD_COLOR)
    if not os.path.exists('./data/photo/'):
        os.makedirs('./data/photo/')
    cv2.imwrite('data/photo/visual-{}.png'.format(time.time()), image)

def show(args):

    pygame.init()
    pygame.font.init()  # 初始化字体模块
    a = pygame.font.SysFont('宋体', 16)
    text = a.render('position:', True, (255, 255, 255), (0, 0, 0))
    text1 = a.render('X:{:.3f}'.format(args.X), True, (255, 255, 255), (0, 0, 0))
    text2 = a.render('Y:{:.3f}'.format(args.Y), True, (255, 255, 255), (0, 0, 0))
    text3 = a.render('Z:{:.3f}'.format(-args.Z), True, (255, 255, 255), (0, 0, 0))
    text_ = a.render('GPS:', True, (255, 255, 255), (0, 0, 0))
    text_1 = a.render('altitude:{:.3f}'.format(args.altitude), True, (255, 255, 255), (0, 0, 0))
    text_2 = a.render('latitude:{:.3f}'.format(args.latitude), True, (255, 255, 255), (0, 0, 0))
    text_3 = a.render('longitude:{:.3f}'.format(args.longitude), True, (255, 255, 255), (0, 0, 0))
    screen = pygame.display.set_mode((200, 200))   # 设置屏幕

    # 设置矩形区域
    ztx, zty, ztw, zth = text.get_rect()
    # 绘制显示文字的矩形区域
    jx = pygame.Rect(5, 50, ztw, zth)

    screen.fill((0, 0, 0))

    # 图像坐标系，左上角为(0, 0)，在此放置图片
    screen.blit(text, [jx.x, jx.y])
    screen.blit(text1, [jx.x, jx.y+20])
    screen.blit(text2, [jx.x, jx.y+40])
    screen.blit(text3, [jx.x, jx.y+60])
    screen.blit(text_,  [jx.x+80, jx.y])
    screen.blit(text_1, [jx.x+80, jx.y+20])
    screen.blit(text_2, [jx.x+80, jx.y+40])
    screen.blit(text_3, [jx.x+80, jx.y+60])

    pygame.display.flip()
    pygame.display.update()

# 将无人机旋转至指定偏航角
def rotateBytargetYaw(targetYam, client, args, vehicle_name=''):
    '''

    :param targetYam: 目标偏航角
    :param client:
    :param args:
    :return:
    '''

    while True:
        msgs = updata_uavdata(client, vehicle_name=vehicle_name)
        deviate_angle = targetYam - msgs[vehicle_name]['yaw']
        if abs(deviate_angle) < 0.5:
            break
        client.rotateByYawRateAsync(deviate_angle * 0.5, 0.5, vehicle_name=vehicle_name)
        time.sleep(0.5)

# 获取路径斜率
def get_path_k(x1, x2, y1, y2):
    '''

    :param x1:
    :param x2:
    :param y1:
    :param y2:
    :return:
    '''
    k = (y2 -y1) / (x2 - x1)
    return k

# 获取路径的xy的平移值
def adjust_distance(div_distance, k):
    '''

    :param div_distance: 当前距离与目标距离的差
    :param k: 斜率
    :return:
    '''

    angle = math.atan(k) + math.pi/2

    delta_x = math.cos(angle) * div_distance
    delta_y = math.sin(angle) * div_distance

    return delta_x, delta_y

# 对路径点进行可视化
def plot_path_point(paths, paths_):
    '''

    :param paths: 初始路径
    :param paths_: 平移后的路径
    :return:
    '''
    # 可视化路径点
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    path1 = np.array(paths)
    path2 = np.array(paths_)
    ax.plot(path1[:, 0], path1[:, 1], path1[:, 2], c=colors[10], label='调整前路径')
    ax.plot(path2[:, 0], path2[:, 1], path2[:, 2], c=colors[30], label='调整后路径')
    ax.set_title('路径调整', fontsize=16)
    ax.legend(loc='upper right', fontsize=12)
    if not os.path.exists('./data/img/'):
        os.makedirs('./data/img/')
    plt.savefig('./data/img/path_point.jpg')

def insert_points(client, point, num, vehicle_name=''):
    '''

    :param point: 目标点
    :param num: 插入点的数量
    :param args:
    :return:
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