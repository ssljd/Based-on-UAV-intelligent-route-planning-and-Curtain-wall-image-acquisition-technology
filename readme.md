# Simulated-UAV（无人机仿真）






#### 资料汇总

| 相关资料 | 链接地址 |
| :-----: | :-----: |
| Airsim官方文档 | [link](https://github.com/microsoft/AirSim) |
| Airsim | [link](https://microsoft.github.io/AirSim/) |
| Airsim环境搭建 | [link](https://blog.csdn.net/qq_41071754/article/details/119561844) |
| Airsim和python环境搭建 | [link](https://blog.csdn.net/dbqwcl/article/details/128618922?csdn_share_tail=%7B%22type%22%3A%22blog%22%2C%22rType%22%3A%22article%22%2C%22rId%22%3A%22128618922%22%2C%22source%22%3A%22unlogin%22%7D) |
| UE4加载本地倾斜模型流程 | [link](https://www.bilibili.com/video/BV1fT4y1v7JE/?share_source=copy_web&vd_source=c1672af9d0b6d625c84667b5a523677a) |
| cesiumlab工具下载 | [link](http://www.cesiumlab.com/) |
| osg2cesiumApp工具下载 | [link](https://www.jianshu.com/p/e1ee883ff7a5) |
| Airsim雷达使用 | [link](https://blog.csdn.net/joeshuai/article/details/122191910) |
| lidar数据获取并显示 | [link](https://ldgcug.github.io/2019/08/30/Airsim/%E5%88%9D%E8%AF%86Airsim%EF%BC%88%E5%8D%81%EF%BC%89%E4%B9%8BLidar%E6%95%B0%E6%8D%AE%E8%8E%B7%E5%8F%96%E5%B9%B6%E6%98%BE%E7%A4%BA/)
 |
|  |  |
| 人工势场法避障 | [link](https://blog.csdn.net/k_kun/article/details/126036987?spm=1001.2014.3001.5502) |


##### 航线规划
- 航线规划 [link](https://www.bilibili.com/video/BV1Fm4y197di/?vd_source=85081344733c0ee5a99dcc8ee941564c)



#### 问题汇总

1. block测试中，输入update_from_git.dat运行报错
> 解决先退出Epic Games launcher，再重新打开Epic launcher, 然后会自动跳出 fix of associate project 的选项

2. Could not find NetFxSDK install dir; this will prevent SwarmInterface from installing. Install a version of .NET Framework SDK at 4.6.0 or higher
> 解决：安装4.6.0及更高版本的.NET Framework SDK

3. 运行引擎需要与D3D11兼容的GPU功能级别11.0,着色器型号5.0
>

