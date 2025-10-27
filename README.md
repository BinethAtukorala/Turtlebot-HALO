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
| `target_distance_m` | double | `2.0`         | Desired follow distance     |
| `max_linear_speed`  | double | `0.6`         | m/s clamp                   |
| `qos_reliability`   | string | `best_effort` | `reliable` or `best_effort` |


## ROS Interfaces (Topics/Services/Actions)

### Topics (Subscribe)

| Topic            | Type                        | QoS            | Notes                  |
| ---------------- | --------------------------- | -------------- | ---------------------- |
| `/scan`          | `sensor_msgs/msg/LaserScan` | SensorData QoS | Required               |
| `/human/error_x` | `std_msgs/msg/Float32`      | Default        | Horizontal pixel error |


### Topics (Publish)

| Topic             | Type                      | QoS     | Notes                  |
| ----------------- | ------------------------- | ------- | ---------------------- |
| `/cmd_vel`        | `geometry_msgs/msg/Twist` | Default | Robot velocity command |
| `/human/distance` | `std_msgs/msg/Int32`      | Default | Estimated range (cm)   |


### Services / Actions

| Service             | Type                        | Notes                  |
| ------------------- | --------------------------- | ---------------------- |
| '/pid'              | `halobot_msgs/msg/PidTuner` | Update kP, kI, kD, kAng values for PID Tuning |

## Open Source Software Used

- [Turtlebot3]()
- [Ultralytics YOLO]()
- [Actor physics collision]()
