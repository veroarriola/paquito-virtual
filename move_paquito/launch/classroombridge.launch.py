"""Launch Gazebo server and client with command line arguments."""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from ros_gz_bridge.actions import RosGzBridge

models_package = 'paquito_models'
package_name = 'move_paquito'

os.environ['GZ_SIM_RESOURCE_PATH'] = \
    os.path.join( get_package_share_directory(models_package),
        'worlds'
    ) + \
    os.pathsep + os.path.join(
        get_package_share_directory(models_package),
        'models'
    )

def generate_launch_description():
    verbose = LaunchConfiguration('v', default='1')
    pkg_launch_arg = DeclareLaunchArgument(
        'v',
        default_value='1'
    )

    # World
    world_file_name = 'classroom-world.sdf'

    world = os.path.join(
        get_package_share_directory(models_package),
        'worlds',
        world_file_name
    )

    # Bridge
    #bridge_name = 'ros_gz_bridge'
    #config_file = 'simplebridge.yaml'
    bridge_config_file = os.path.join(
        get_package_share_directory(package_name),
        'resource',
        'simplebridge.yaml'
    )
    ros_topic_name='/keyboard/keypress'
    ros_msg_type='std_msgs/msg/Int32'
    gz_msg_type='gz.msgs.Int32'

    # Launch description
    ld =  LaunchDescription([
        pkg_launch_arg,
        ExecuteProcess(
            cmd=['gz', 'sim', '-v', verbose, world_file_name],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            #arguments=[ ros_topic_name + '@' + ros_msg_type + '@' + gz_msg_type],
            arguments=[
                '--ros-args',
                '-p',
                f'config_file:={bridge_config_file}',
            ],
            output='screen',
        ),
        ExecuteProcess(
            cmd=['ros2', 'topic', 'echo', '/keyboard/keypress'],
            output='screen'
        ),
    ])

    print("\033[33mEn Gazebo abre el plugin Key Publisher\033[0m")

    return ld

