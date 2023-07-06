import cv2
import time
import airsim
import argparse
import threading
from utils import *
from path import *
import keyboard
from lidar import *
from airsim_avoid_APF import move_by_path_and_avoid_APF
from airsim_tracking_carrot import move_by_path_3d

def path_fly(client, paths, args, vehicle_name=''):
    # 测量与建筑物的距离，调整路径
    lidar = LidarTest(client, vehicle_name=vehicle_name)
    distance = lidar.get_distance()
    paths_ = vertical_move_path(paths, args.k, distance[vehicle_name] - args.target_distance)

    # 执行贴近摄影路径飞行g
    # client.startRecording()
    for path in paths_:
        x, y, z = path[0], path[1], -path[2]
        if vehicle_name == 'Drone2':
            z += 20
        print(x, y, z)
        # 执行飞行操作
        client.moveToPositionAsync(x, y, z, 1, vehicle_name=vehicle_name)
        lidar.get_distance()
        while True:
            pose = client.simGetVehiclePose(vehicle_name=vehicle_name)
            position = pose.position
            x_error = x - position.x_val
            y_error = y - position.y_val
            z_error = z - position.z_val
            print(x_error, y_error, z_error)
            if abs(x_error) < 0.5 and abs(y_error) < 0.5 and abs(z_error) < 0.5:
                # saveimg(client, args)
                break
            time.sleep(1)
    # client.startRecording()

def task(client, path, args, vehicle_name=''):

    # 每1秒检查一次连接状态，并在控制台中报告，以便用户可以查看连接的进度（应该是开启了个线程，因为只是调用了一次）
    client.confirmConnection()

    # get control
    client.enableApiControl(True, vehicle_name=vehicle_name)
    print("get control")
    # unlock
    client.armDisarm(True, vehicle_name=vehicle_name)
    print("unlock")
    # 无人机起飞
    client.takeoffAsync(vehicle_name=vehicle_name).join()
    print("takeoff")

    # 还存在一些问题，需要改进
    # client.simPlotPoints(points, color_rgba=[0, 1, 0, 1], size=30, is_persistent=True)
    # client.simPlotLineStrip(points, color_rgba=[0, 1, 0, 1], thickness=5, is_persistent=True)
    # move_by_path_3d(client, points, delta=0.5, a0=2, dt=0.12, K0=1, K1=2, K2=0.8)

    if vehicle_name == 'Drone1':

        paths1 = init_path(path, args)
        # 飞行到指定目标点，带有避障功能
        # points = insert_points(client, paths1[0], 20, vehicle_name=vehicle_name)
        # move_by_path_and_avoid_APF(client, points, K_track=[1.5, 6, 1], delta=5, K_avoid=[3, 60], Q_search=8, epsilon=1,
        #                            Ul=[2, 3], dt=0.3, vehicle_name=vehicle_name)
        # 调整无人机的姿态
        client.moveToPositionAsync(paths1[0][0], paths1[0][1], -paths1[0][2], 2, vehicle_name=vehicle_name).join()
        rotateBytargetYaw(args.target_yal - 90, client, args, visual=True, vehicle_name=vehicle_name)
        # 按路径飞行
        path_fly(client, paths1, args, vehicle_name=vehicle_name)
        # 返航
        # points = insert_points([0.5, 0.5, -2], 100, args)
        # move_by_path_and_avoid_APF(client, [airsim.Vector3r(0.5, 0.5, -2)], K_track=[1.5, 6, 1], delta=5, K_avoid=[3, 60],
        #                            Q_search=8, epsilon=1,
        #                            Ul=[2, 3], dt=0.3, vehicle_name=vehicle_name)

        client.moveToPositionAsync(-1, -1, 0, 2, vehicle_name=vehicle_name).join()
        # 无人机降落
        client.landAsync(vehicle_name=vehicle_name).join()
        print("land")
        # lock
        client.armDisarm(False, vehicle_name=vehicle_name)
        print("lock")
        # release control
        client.enableApiControl(False, vehicle_name=vehicle_name)
        print("release control")

    elif vehicle_name == 'Drone2':
        paths2 = init_path(path, args)
        # 飞行到指定目标点，带有避障功能
        # points = insert_points(client, paths2[0], 20, args)
        # move_by_path_and_avoid_APF(client, points, K_track=[1.5, 6, 1], delta=5, K_avoid=[3, 60], Q_search=8, epsilon=1,
        #                            Ul=[2, 3], dt=0.3, vehicle_name=vehicle_name)
        # 调整无人机的姿态
        client.moveToPositionAsync(paths2[0][0], paths2[0][1], -paths2[0][2] + 20, 2, vehicle_name=vehicle_name).join()
        rotateBytargetYaw(args.target_yal - 90, client, args, vehicle_name=vehicle_name)
        # 按路径飞行
        path_fly(client, paths2, args, vehicle_name=vehicle_name)
        # 返航
        # points = insert_points([0.5, 0.5, -2], 100, args)
        # move_by_path_and_avoid_APF(client, [airsim.Vector3r(0.5, 0.5, -2)], K_track=[1.5, 6, 1], delta=5, K_avoid=[3, 60],
        #                            Q_search=8, epsilon=1,
        #                            Ul=[2, 3], dt=0.3, vehicle_name=vehicle_name)

        client.moveToPositionAsync(1, 1, 0, 2, vehicle_name=vehicle_name).join()
        # 无人机降落
        client.landAsync(vehicle_name=vehicle_name).join()
        print("land")
        # lock
        client.armDisarm(False, vehicle_name=vehicle_name)
        print("lock")
        # release control
        client.enableApiControl(False, vehicle_name=vehicle_name)
        print("release control")

def execute():
    args = parse()
    client1 = airsim.MultirotorClient()
    # client2 = airsim.MultirotorClient()
    thread1 = threading.Thread(target=task, args=(client1, './path/5_Region_0.19cm_5(0).kml', args, 'Drone1'))
    # thread2 = threading.Thread(target=task, args=(client2, './path/5_Region_0.19cm_5(1).kml', args, 'Drone2'))
    thread1.start()
    # thread2.start()

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cameraType', type=str, default='scene', help='选择要采集的图像类型, 正常画面 12fps  1920*1080')
    parser.add_argument('--cameraUse', type=str, default='1', help='无人机自带5个相机，其ID 与相机分别对应如下: 0 = front_center; 1 = front_right; 2 = front_left; 3 = bottom_center #下视画面; 4 = back_center')
    parser.add_argument('--IP', type=str, default="127.0.0.1", help='局域网主机IP')
    parser.add_argument('--api_control', type=bool, default=True, help='是否开启api控制，默认是false')
    parser.add_argument('--mode', type=int, default=1, help='图像采集模式-0：定点拍摄采集；1：图像录制采集')
    parser.add_argument('--init_place', type=list, default=[29.925371, 121.626648], help='出生位置，GPS坐标')
    parser.add_argument('--rate', type=float, default=0.5, help='调整率')
    parser.add_argument('--k', type=float, default=0, help='路径斜率')
    parser.add_argument('--target_distance', type=float, default=5, help='与建筑间的目标距离')
    parser.add_argument('--target_yaw', type=float, default=0.0, help='目标偏航角')
    parser.add_argument('--target_pitch', type=float, default=0.0, help='目标俯仰角')

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    execute()