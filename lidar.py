import os
import airsim
import math
import pprint
import numpy
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Makes the drone fly and get Lidar data
class LidarTest:

    def __init__(self, client, vehicle_name=''):

        # connect to the AirSim simulator
        self.client = client
        self.vehicle_name = vehicle_name

    # 获取无人机的xyz坐标，为后面计算距离做准备
    def get_drone_position(self, lidarData):
        position = lidarData.pose.position

        return position

    # 将点云数据转换成相应角度和距离
    def point_cloud_to_angle_position(self, pos, points):
        obs_distance = []
        angles = []
        for i in range(len(points)):
            x = round(points[i][0], 2)
            y = round(points[i][1], 2)
            z = round(points[i][2], 2)
            if x != 0:
                angle = math.atan(y / x) * 180 / 3.14  # 利用三角函数关系求当前角度
                angle = math.floor(angle)  # 向下取整
                angles.append(angle)
                # distance = math.sqrt(
                #     (pos.x_val - x) ** 2 + (pos.y_val - y) ** 2 + (pos.z_val - z) ** 2)  # 根据激光点坐标和无人机当前点坐标求解距离
                distance = math.sqrt(
                    x ** 2 + y ** 2 + z ** 2)
                obs_distance.append(distance)
        # angles, obs_distance = self.scale_point_cloud(angles, obs_distance)  # 进行相应变换
        return angles, obs_distance

    # 在180度范围内，每隔1度，取一个值，即将会取181个值（中间有0度）
    # 对每个角度，求出其对应的下标有哪些，然后求均值，表示当前角度的激光点距离
    def scale_point_cloud(self, angles, obs_distance):
        angle_min = -90.0
        angle_max = 90.0
        new_angles = []
        new_obs_distance = []
        # address_index = [x for x in range(len(list_position_name)) if list_position_name[x] == i]
        for i in range(int(angle_max - angle_min + 1)):
            address_index = [x for x in range(len(angles)) if angles[x] == angle_min + i]  # 求每个角度的下标
            if len(address_index) == 0:  # 如果某个角度没有值，则直接给最大值
                distance = 100.0
            else:  # 否则，求均值
                total_dis = 0
                for j in range(len(address_index)):
                    total_dis += obs_distance[address_index[j]]
                distance = total_dis / len(address_index)
            new_angles.append(angle_min + i)
            new_obs_distance.append(distance)
        return new_angles, new_obs_distance

    def get_distance(self):
        if self.vehicle_name == 'Drone1':
            lidar_name = 'Lidar1'
        elif self.vehicle_name == 'Drone2':
            lidar_name = 'Lidar2'
        lidarData = self.client.getLidarData(vehicle_name=self.vehicle_name)

        if (len(lidarData.point_cloud) < 3):
            print("\tNo points received from Lidar data")
            return numpy.array([0, 0, 0])
        else:

            pos = self.get_drone_position(lidarData)
            points = self.parse_lidarData(lidarData)
            angles, obs_distance = self.point_cloud_to_angle_position(pos, points)
            new_angles, new_obs_distance = self.scale_point_cloud(angles, obs_distance)
            distance = {}
            if self.vehicle_name == 'Drone1':
                distance[self.vehicle_name] = min(obs_distance)
                print("\t{}: min_distance: {}".format(self.vehicle_name, min(obs_distance)))
            elif self.vehicle_name == 'Drone2':
                print("\t{}：min_distance: {}".format(self.vehicle_name, min(obs_distance)))
                distance[self.vehicle_name] = min(obs_distance)
            return distance

            # print("\tnew_angles: {} new_obs_distance: {}".format(angles, obs_distance))
            # print("\t\tlidar position: %s" % (pprint.pformat(lidarData.pose.position)))
            # print("\t\tlidar orientation: %s" % (pprint.pformat(lidarData.pose.orientation)))
            # self.saveimg(points)

    # 将雷达数据转化为点云数据
    def parse_lidarData(self, data):
        '''

        :param data: 激光雷达检测到的数据
        :return:
        '''

        # reshape array of floats to array of [X,Y,Z]
        points = numpy.array(data.point_cloud, dtype=numpy.dtype('f4'))
        points = numpy.reshape(points, (int(points.shape[0] / 3), 3))

        return points

    # 保存点云图
    def saveimg(self, points):

        # 可视化点云数据
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1, c=points[:, 2])
        if not os.path.exists('./data/point_cloud/'):
            os.makedirs('./data/point_cloud/')
        plt.savefig('./data/point_cloud/{}_point.jpg'.format(time.time()))
