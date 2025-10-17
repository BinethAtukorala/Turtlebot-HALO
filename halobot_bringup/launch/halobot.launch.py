from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='halobot_bringup',
            executable='tracker',
            name='tracker',
            output='screen',
        ),
    ])
