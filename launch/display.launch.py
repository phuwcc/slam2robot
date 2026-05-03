import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')
    xacro_file = os.path.join(pkg_share, 'urdf', 'slam2robot.urdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'robot.rviz')
    controller_config_file = os.path.join(pkg_share, 'config', 'controllers.yaml')

    robot_description_config = xacro.process_file(xacro_file)
    robot_desc = robot_description_config.toxml().replace(
        '__CONTROLLER_CONFIG_FILE__',
        controller_config_file,
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        condition=IfCondition(LaunchConfiguration('start_robot_state_publisher')),
    )

    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(LaunchConfiguration('start_joint_state_publisher_gui')),
    )

    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(LaunchConfiguration('start_rviz')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('start_robot_state_publisher', default_value='false'),
        DeclareLaunchArgument('start_joint_state_publisher_gui', default_value='false'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('rviz_config', default_value=rviz_config_file),
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz2
    ])
