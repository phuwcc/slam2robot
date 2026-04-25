import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')
    config_dir = os.path.join(pkg_share, 'config')
    rviz_config = os.path.join(pkg_share, 'rviz', 'robot.rviz')
    default_map_dir = os.path.join(pkg_share, 'maps', 'slam_map')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_gazebo = LaunchConfiguration('start_gazebo')
    start_slam = LaunchConfiguration('start_slam')
    start_rviz = LaunchConfiguration('start_rviz')
    save_map = LaunchConfiguration('save_map')
    map_file = LaunchConfiguration('map_file')
    free_thresh = LaunchConfiguration('free_thresh')
    occupied_thresh = LaunchConfiguration('occupied_thresh')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'gazebo.launch.py')
        ),
        condition=IfCondition(start_gazebo),
    )

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '-configuration_directory', config_dir,
            '-configuration_basename', 'cartographer_2d.lua',
        ],
        remappings=[('scan', '/scan')],
        condition=IfCondition(start_slam),
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='occupancy_grid_node',
        name='occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-resolution', '0.05', '-publish_period_sec', '1.0'],
        condition=IfCondition(start_slam),
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(start_rviz),
    )

    save_map_log = LogInfo(
        msg=['Saving map to: ', map_file],
        condition=IfCondition(save_map),
    )

    save_map_node = Node(
        package='nav2_map_server',
        executable='map_saver_cli',
        name='map_saver_cli',
        output='screen',
        arguments=[
            '-f', map_file,
            '--free', free_thresh,
            '--occ', occupied_thresh,
        ],
        condition=IfCondition(save_map),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('start_gazebo', default_value='true'),
        DeclareLaunchArgument('start_slam', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('save_map', default_value='false'),
        DeclareLaunchArgument('map_file', default_value=default_map_dir),
        DeclareLaunchArgument('free_thresh', default_value='0.25'),
        DeclareLaunchArgument('occupied_thresh', default_value='0.65'),
        gazebo_launch,
        cartographer_node,
        occupancy_grid_node,
        rviz2_node,
        save_map_log,
        save_map_node,
    ])
