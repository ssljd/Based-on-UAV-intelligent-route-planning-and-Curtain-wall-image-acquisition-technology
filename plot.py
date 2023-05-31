import os
import pygame
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

# 颜色列表
colors = []
for name, hex in matplotlib.colors.cnames.items():
    colors.append(name)


# 将无人机的位置信息进行实时显示
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


# 对无人机的偏航角的调整过程进行可视化
def plot_yaw(times, yaws, target_yaw, error):
    '''

    :param times: 事件列表
    :param yaws:  偏航角列表
    :param target_yaw: 目标偏航角
    :param error: 允许的误差
    :return:
    '''

    target_yaws = [target_yaw for i in range(len(times))]
    up_error = [target_yaw + error for i in range(len(times))]
    down_error = [target_yaw - error for i in range(len(times))]
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(8, 4), dpi=300)
    plt.plot(times, target_yaws, color='r', linewidth=0.5, linestyle='-', label='Target-yaw')
    plt.plot(times, up_error, color='k', linewidth=0.5, linestyle='--', label='Up-error')
    plt.plot(times, down_error, color='k', linewidth=0.5, linestyle='--', label='Down-error')
    plt.plot(times, yaws, color='b', linewidth=0.5, linestyle='-', label='yaw')
    plt.xlabel('time(s)', fontsize=6)
    plt.ylabel('yaw', fontsize=6)
    plt.legend(loc='upper right', fontsize=6)
    plt.ylim(0, 80)
    plt.savefig('./data/img/yaw.jpg')
