from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='human_tracker',
            executable='human_tracker_node',
            name='human_tracker_node',
            output='screen',
        ),
    ])
