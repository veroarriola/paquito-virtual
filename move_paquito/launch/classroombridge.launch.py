"""Launch Gazebo server and client with command line arguments."""

import os
from termcolor import colored
from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from ros_gz_bridge.actions import RosGzBridge


# Packages
package_name = 'move_paquito'
models_package = 'paquito_models'

# World
world_models_path = os.path.join(
    get_package_share_directory(models_package),
    'worlds'
)
world_file_name = 'classroom-world.sdf'
world_name = 'car_world'

# Robot
robot_models_path = os.path.join(
    get_package_share_directory(models_package),
    'models'
)
robot_model_path = os.path.join(
    robot_models_path,
    'paquito',
    'paquito_model.sdf'
)
gz_spawn_model_launch_source = os.path.join(
    get_package_share_directory('ros_gz_sim'),
    "launch",
    "gz_spawn_model.launch.py"
)
robot_entity_name = 'paquito_bot'

# .-. Environment variables por Gazebo -.-

# Resources

print(colored(os.environ['GZ_SIM_RESOURCE_PATH'], 'yellow'))
print()
os.environ['GZ_SIM_RESOURCE_PATH'] = \
    world_models_path + os.pathsep + \
    robot_models_path + os.pathsep + \
    os.environ['GZ_SIM_RESOURCE_PATH']
print(colored(os.environ['GZ_SIM_RESOURCE_PATH'], 'yellow'))

# Local drivers

os.environ['GZ_SIM_SYSTEM_PLUGIN_PATH'] = \
    os.path.join( get_package_prefix('gz_mecanum_drive_controller'),
        'lib/gz_mecanum_drive_controller/'
    )


def generate_launch_description():
    verbose = LaunchConfiguration('v', default='1')
    pkg_launch_arg = DeclareLaunchArgument(
        'v',
        default_value='1'
    )

    # Bridge
    bridge_config_file = os.path.join(
        get_package_share_directory(package_name),
        'resource',
        'simplebridge.yaml'
    )

    # Launch description
    ld = LaunchDescription([
        pkg_launch_arg,
        DeclareLaunchArgument(name='use_sim_time', default_value='True', description='Flag to enable use_sim_time'),
        DeclareLaunchArgument(name='model', default_value=robot_model_path, description='Absolute path to robot model file'),
        ExecuteProcess(
            cmd=['gz', 'sim', '-v', verbose, world_file_name],
            output='screen',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'robot_description': ParameterValue(Command(['xacro ', LaunchConfiguration('model')]), value_type=str)},
                {'use_sim_time': LaunchConfiguration('use_sim_time')}
            ]
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
            launch_arguments={
                'world': world_name,
                'topic': '/robot_description',
                'entity_name': robot_entity_name,
            }.items(),
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '--ros-args',
                '-p',
                f'config_file:={bridge_config_file}',
            ],
            output='screen',
        ),
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen'
        ),
        Node(
            package='game_control',
            executable='game_control_node',
            name='game_control',
            output='screen',
        ),
        ExecuteProcess(
            cmd=['ros2', 'topic', 'echo', '/keyboard/keypress'],
            output='screen'
        ),
    ])

    print("\033[33mEn Gazebo abre el plugin Key Publisher\033[0m")

    return ld

