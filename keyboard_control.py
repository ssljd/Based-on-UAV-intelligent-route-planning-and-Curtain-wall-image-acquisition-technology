import airsim
import cv2
import time
from utils import *
from path import *
import keyboard

cameraTypeMap = {
    "depth": airsim.ImageType.DepthVis,  # 黑白景深图像
    "segmentation": airsim.ImageType.Segmentation,  # 彩色目标分割图像
    "seg": airsim.ImageType.Segmentation,  # 彩色目标分割图像
    "scene": airsim.ImageType.Scene,  # 正常图像
    "disparity": airsim.ImageType.DisparityNormalized,
    "normals": airsim.ImageType.SurfaceNormals
}

# 键盘控制回调函数
def callBackFunc(x):
    w = keyboard.KeyboardEvent('down', 28, 'w')             # 前进
    s = keyboard.KeyboardEvent('down', 28, 's')             # 后退
    a = keyboard.KeyboardEvent('down', 28, 'a')             # 左移
    d = keyboard.KeyboardEvent('down', 28, 'd')             # 右移
    up = keyboard.KeyboardEvent('down', 28, 'up')           # 上升
    down = keyboard.KeyboardEvent('down', 28, 'down')       # 下降
    left = keyboard.KeyboardEvent('down', 28, 'left')       # 左转
    right = keyboard.KeyboardEvent('down', 28, 'right')     # 右转
    photo = keyboard.KeyboardEvent('down', 28, 'enter')     # 拍照
    r = keyboard.KeyboardEvent('down', 28, 'r')             # 开始录制
    q = keyboard.KeyboardEvent('down', 28, 'q')             # 停止录制
    k = keyboard.KeyboardEvent('down', 28, 'k')             # 获取控制
    l = keyboard.KeyboardEvent('down', 28, 'l')             # 释放控制

    if x.event_type == 'down' and x.name == w.name:
        # 前进
        client.moveByVelocityBodyFrameAsync(3, 0, 0, 0.5)
        print("前进")
    elif x.event_type == 'down' and x.name == s.name:
        # 后退
        client.moveByVelocityBodyFrameAsync(-3, 0, 0, 0.5)
        print("后退")
    elif x.event_type == 'down' and x.name == a.name:
        # 左移
        client.moveByVelocityBodyFrameAsync(0, -2, 0, 0.5)
        print("左移")
    elif x.event_type == 'down' and x.name == d.name:
        # 右移
        client.moveByVelocityBodyFrameAsync(0, 2, 0, 0.5)
        print("右移")
    elif x.event_type == 'down' and x.name == up.name:
        # 上升
        client.moveByVelocityBodyFrameAsync(0, 0, -0.5, 0.5)
        print("上升")
    elif x.event_type == 'down' and x.name == down.name:
        # 下降
        client.moveByVelocityBodyFrameAsync(0, 0, 0.5, 0.5)
        print("下降")
    elif x.event_type == 'down' and x.name == left.name:
        # 左转
        client.rotateByYawRateAsync(-20, 0.5)
        print("左转")
    elif x.event_type == 'down' and x.name == right.name:
        # 右转
        client.rotateByYawRateAsync(20, 0.5)
        print("右转")
    elif x.event_type == 'down' and x.name == k.name:
        # 无人机起飞
        # get control
        client.enableApiControl(True)
        print("get control")
        # unlock
        client.armDisarm(True)
        print("unlock")
        # Async methods returns Future. Call join() to wait for task to complete.
        client.takeoffAsync().join()
        print("takeoff")
    elif x.event_type == 'down' and x.name == l.name:
        # 无人机降落
        client.landAsync().join()
        print("land")
        # lock
        client.armDisarm(False)
        print("lock")
        # release control
        client.enableApiControl(False)
        print("release control")
    elif x.event_type == 'down' and x.name == photo.name:
        saveimg(client, cameraTypeMap, args)
        print('photo')
    elif x.event_type == 'down' and x.name == r.name:
        client.startRecording()
        print('开始录制')
    elif x.event_type == 'down' and x.name == q.name:
        client.stopRecording()
        print('停止录制')
    else:
        # 没有按下按键
        client.moveByVelocityBodyFrameAsync(0, 0, 0, 0.5).join()
        client.hoverAsync().join()  # 第四阶段：悬停6秒钟
        print("悬停")

if __name__ == "__main__":
    client = airsim.MultirotorClient()
    # 每1秒检查一次连接状态，并在控制台中报告，以便用户可以查看连接的进度（应该是开启了个线程，因为只是调用了一次）
    client.confirmConnection()

    while True:
        # 监听键盘事件，执行回调函数
        keyboard.hook(callBackFunc)
        keyboard.wait()
