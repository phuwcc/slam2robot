import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')
    pkg_tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    world_path = os.path.join(pkg_tb3_gazebo, 'worlds', 'turtlebot3_world.world')
    workspace_models_path = os.path.join(pkg_share, '..')

    controller_config_file = os.path.join(pkg_share, 'config', 'controllers.yaml')
    xacro_file = os.path.join(pkg_share, 'urdf', 'slam2robot.urdf')
    robot_desc = xacro.process_file(xacro_file).toxml().replace(
        "__CONTROLLER_CONFIG_FILE__",
        controller_config_file,
    )

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            os.environ.get('GAZEBO_MODEL_PATH', ''), 
            ':', workspace_models_path,
            ':', os.path.join(pkg_tb3_gazebo, 'models')
        ]
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items()
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description', 
            '-entity', 'my_robot',
            '-x', '-2.0', '-y', '-0.5', '-z', '0.01'
        ],
        output='screen'
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "-c", "/controller_manager",
            "--param-file", controller_config_file,
        ],
        output='screen'
    )

    joint_position_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_position_controller",
            "-c", "/controller_manager",
            "--param-file", controller_config_file,
        ],
        output='screen'
    )

    load_joint_state_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    load_joint_position_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[joint_position_controller_spawner],
        )
    )

    return LaunchDescription([
        set_gazebo_model_path,
        robot_state_publisher,
        gazebo,
        spawn_entity,
        load_joint_state_broadcaster,
        load_joint_position_controller,
    ])
