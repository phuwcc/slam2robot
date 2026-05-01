import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'start_gazebo': LaunchConfiguration('start_gazebo'),
            'start_slam': LaunchConfiguration('start_slam'),
            'start_rviz': LaunchConfiguration('start_rviz'),
            'save_map': LaunchConfiguration('save_map'),
            'world': LaunchConfiguration('world'),
            'slam': 'cartographer',
            'map_file': LaunchConfiguration('map_file'),
            'free_thresh': LaunchConfiguration('free_thresh'),
            'occupied_thresh': LaunchConfiguration('occupied_thresh'),
            'spawn_x': LaunchConfiguration('spawn_x'),
            'spawn_y': LaunchConfiguration('spawn_y'),
            'spawn_z': LaunchConfiguration('spawn_z'),
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('start_gazebo', default_value='true'),
            DeclareLaunchArgument('start_slam', default_value='true'),
            DeclareLaunchArgument('start_rviz', default_value='true'),
            DeclareLaunchArgument('save_map', default_value='false'),
            DeclareLaunchArgument('world', default_value='world_1'),
            DeclareLaunchArgument('map_file', default_value=os.path.join(pkg_share, 'maps', 'slam_map')),
            DeclareLaunchArgument('free_thresh', default_value='0.25'),
            DeclareLaunchArgument('occupied_thresh', default_value='0.65'),
            DeclareLaunchArgument('spawn_x', default_value='-2.0'),
            DeclareLaunchArgument('spawn_y', default_value='-0.5'),
            DeclareLaunchArgument('spawn_z', default_value='0.01'),
            gazebo_launch,
        ]
    )
