from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration


from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    ld = LaunchDescription()

    # Get path to directories
    pkg_name = 'halobot_bringup'
    pkg_path = FindPackageShare(pkg_name)

    # command line arguments
    sim_launch_arg = DeclareLaunchArgument(
        'sim',
        default_value='False',
        description='Flag to enable sim'
    )
    ld.add_action(sim_launch_arg)

    tracker_node = Node(
        package=pkg_name,
        executable='tracker',
        name='tracker',
        output='screen',
        parameters=[{'sim': LaunchConfiguration('sim')}]
    )

    ld.add_action(tracker_node)
    
    follower_node = Node(
        package=pkg_name,
        executable='follower',
        name='follower',
        output='screen'
    )

    ld.add_action(follower_node)

    range_finder_node = Node(
        package=pkg_name,
        executable='range_finder',
        name='range_finder',
        output='screen'
    )

    ld.add_action(range_finder_node)

    return ld
