#!/usr/bin/env python3
"""
Standalone Cartographer launch file for testing with rosbag.
This launch file runs only the Cartographer SLAM without Gazebo simulation.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')
    cartographer_config_dir = os.path.join(pkg_share, 'config')
    
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=[
            '-configuration_directory',
            cartographer_config_dir,
            '-configuration_basename',
            'cartographer_2d.lua',
        ],
        remappings=[('scan', '/scan')],
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-resolution', '0.05', '-publish_period_sec', '1.0'],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                description='Use simulated time (important for rosbag playback)',
            ),
            cartographer_node,
            occupancy_grid_node,
        ]
    )
