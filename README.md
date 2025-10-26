# TurtleBot HALO - Hauling Assistant with Locating Operations
Turtlebot follows a person. A project for 41014 Sensors and Control for Mechatronic Systems.

[![ROS 2](https://img.shields.io/badge/ROS2-Humble-blue)]() [![Python](https://img.shields.io/badge/Python-3.10-blue)]()
[![Ultralytics YOLO](https://img.shields.io/badge/Ultralytics%20YOLO-v11-blue)](https://github.com/ultralytics/ultralytics)

## Features
- Tracks a person using RGB Camera + LiDAR.
- Stops movement when within a predefined distance from the target and restarts the movement when target leaves the area.
- Full featured simulation with animated actors with physics collision implemented.

## Quickstart

Installation and usage instructions for HALO bot.

### Install


#### ROS 2
- Please follow official installation instructions for ROS2 Humble Hawksbill. [Instructions](https://docs.ros.org/en/humble/Installation.html)



#### Turtlebot

- Official installation guide for setting up Turtlebot3 Waffle Pi and remote PC for communicating with the Turtlebot can be found in the [E-Manual](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/) provided by ROBOTIS.

#### HALO

1. Create a workspace and clone repository.

```bash
mkdir -p ~/turtlebot_ws/src && cd ~/turtlebot_ws/src
https://github.com/BinethAtukorala/Turtlebot-HALO.git
```

2. Build and source
```bash
cd ~/turtlebot_ws/
colcon build --symlink-install
source install/setup.bash
```

### Usage

The package allows the nodes to be run on the real-life robot and the simulation. Due to implementation inconsistencies found in Turtlebot3 code, two configurations were needed to seamlessly switch between the real-life robot and the simulation.

#### Executing on Real-Life Turtlebot3

1. Ensure Turtlebot and Remote PC share same ROS Domain ID. (Default value is 30)

```bash
export ROS_DOMAIN_ID=30
```

2. Run HALO launch file

```bash
ros2 launch halobot_bringup halobot.launch.py
```

The robot will start tracking a human and following them.

> [!WARNING]
> Even though the follower node is meant to stop the robot's movement upon exit, it may fail occasionally to do so. We reccommend having a teleop window standby to stop the robot if needed.

#### Executing on Gazebo Simulation

1. Run Gazebo simulation on desired world. `turtlebot3_house` has been modified to spawn the robot inside the house with animated actors with physics collision.

```bash
ros2 launch turtlebot3_gazebo turtlebot3_house.launch.py
```

2. Run HALO launch file with simulation argument

```bash
ros2 launch halobot_bringup halobot.launch.py sim:=True
```
#### Change parameters at runtime

```bash
ros2 param set /<node_name> <parameter_name> <value>
```

Example:
```bash
ros2 param set /follower max_linear_speed 0.5
```

## ROS Nodes and Parameters

| Name                | Type   | Default       | Description                 | Node |
| ------------------- | ------ | ------------- | --------------------------- | ---- |
| `sim` | boolean | `False`         | Use simulation topics     | Tracker |
| `img_width`  | integer | `600`         | Image width for sectors                   | Range Finder |
| `no_of_sectors`   | integer | `5` | Number of sectors to split the image | Range Finder |
| `front_arc`   | integer | `90` | Arc in front to scan with Lidar (deg) | Range Finder |
| `max_linear_speed`   | double | `0.5` | Maximum linear speed during following | Follower |
| `max_angular_speed`   | double | `0.5` | Maximum angular speed during following | Follower |
| `kP`   | double | `0.4` | Proportional constant of PID controller | Follower |
| `kI`   | double | `0.0` | Integral constant of PID controller | Follower |
| `kD`   | double | `0.0` | Derivative constant of PID tucontrollerner | Follower |
| `kAng`   | double | `0.02` | Angular constant of PID controller | Follower |
| `stopping_distance`   | double | `0.3` | Distance from target to stop movement | Follower |



## ROS Interfaces (Topics/Services/Actions)

### Topics (Subscribe)

| Topic            | Type                        | QoS            | Notes                  |
| ---------------- | --------------------------- | -------------- | ---------------------- |
| `/scan`          | `sensor_msgs/msg/LaserScan` | SensorData QoS | Required               |
| `/image_raw/compressed` | `sensor_msgs/msg/Image` | Default | Compressed image from camera |
| `/human/error_x` | `std_msgs/msg/Int32MultiArray`      | Default        | Horizontal pixel error array |
| `/human/cover` | `std_msgs/msg/Int32`      | Default        | Percentage of screen covered by target |
| `/human/at_target` | `std_msgs/msg/Int32 | Default | Error from center to selected target from array |



### Topics (Publish)

| Topic             | Type                      | QoS     | Notes                  |
| ----------------- | ------------------------- | ------- | ---------------------- |
| `/cmd_vel`        | `geometry_msgs/msg/Twist` | Default | Robot velocity command |
| `/human/error_x` | `std_msgs/msg/Int32MultiArray` | Horizontal pixel error array |
| `/human/cover` | `std_msgs/msg/Int32`      | Default        | Percentage of screen covered by target |
| `/human/at_target` | `std_msgs/msg/Int32 | Default | Error from center to selected target from array |
| `/human/closest_distance` | `std_msgs/msg/Float32 | Default | Distance to closest human |


### Services / Actions

| Service             | Type                        | Notes                  |
| ------------------- | --------------------------- | ---------------------- |
| `/pid`              | `halobot_msgs/msg/PidParam` | Update kP, kI, kD, kAng values for PID Tuning |

## Open Source Software Used

- [Turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- [Actor physics collision](https://github.com/JiangweiNEU/actor_collisions)
