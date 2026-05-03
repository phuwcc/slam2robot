import os

import xacro
from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


VALID_WORLDS = {f'world_{index}': f'world_{index}.world' for index in range(1, 6)}
VALID_SLAM = {'cartographer', 'slam_toolbox'}
DISABLED_MAP_VALUES = {'', 'none', 'false', 'no'}
WORLD_SPAWN_DEFAULTS = {
    'world_1': ('-2.0', '-0.5', '0.01'),
    'world_2': ('2.0', '0.0', '0.01'),
    'world_3': ('-2.0', '-0.5', '0.01'),
    'world_4': ('-2.0', '-0.5', '0.01'),
    'world_5': ('-2.0', '-0.5', '0.01'),
}


def _resolve_selected_map(pkg_share, selected_map):
    normalized_map = selected_map.strip()
    if normalized_map.lower() in DISABLED_MAP_VALUES:
        return None

    candidate_paths = []
    if os.path.isabs(normalized_map):
        candidate_paths.append(normalized_map)
    else:
        candidate_paths.append(os.path.join(pkg_share, 'map', normalized_map))
        if not normalized_map.endswith('.yaml'):
            candidate_paths.append(os.path.join(pkg_share, 'map', f'{normalized_map}.yaml'))

    for candidate_path in candidate_paths:
        if os.path.isfile(candidate_path):
            return candidate_path

    raise RuntimeError(
        "Invalid selected_map '{}'. Expected an existing .yaml file in '{}' or an absolute path.".format(
            selected_map, os.path.join(pkg_share, 'map')
        )
    )


def _resolve_map_output_prefix(pkg_share, map_file):
    normalized_map_file = map_file.strip()
    if not normalized_map_file:
        raise RuntimeError('map_file must not be empty.')

    if os.path.isabs(normalized_map_file):
        resolved_path = normalized_map_file
    else:
        resolved_path = os.path.join(pkg_share, 'map', normalized_map_file)

    root_path, extension = os.path.splitext(resolved_path)
    if extension in {'.yaml', '.pgm'}:
        resolved_path = root_path

    return os.path.normpath(resolved_path)


def _resolve_spawn_pose(selected_world, spawn_x, spawn_y, spawn_z):
    default_spawn_x, default_spawn_y, default_spawn_z = WORLD_SPAWN_DEFAULTS[selected_world]

    resolved_spawn_x = default_spawn_x if spawn_x.strip().lower() == 'auto' else spawn_x
    resolved_spawn_y = default_spawn_y if spawn_y.strip().lower() == 'auto' else spawn_y
    resolved_spawn_z = default_spawn_z if spawn_z.strip().lower() == 'auto' else spawn_z

    return resolved_spawn_x, resolved_spawn_y, resolved_spawn_z


def _launch_setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory('slam2robot')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    selected_world = LaunchConfiguration('world').perform(context)
    selected_slam = LaunchConfiguration('slam').perform(context)
    selected_map = LaunchConfiguration('selected_map').perform(context)
    map_file = LaunchConfiguration('map_file').perform(context)
    spawn_x = LaunchConfiguration('spawn_x').perform(context)
    spawn_y = LaunchConfiguration('spawn_y').perform(context)
    spawn_z = LaunchConfiguration('spawn_z').perform(context)

    if selected_world not in VALID_WORLDS:
        raise RuntimeError(
            f"Invalid world '{selected_world}'. Valid options: {', '.join(VALID_WORLDS)}"
        )

    if selected_slam not in VALID_SLAM:
        raise RuntimeError(
            f"Invalid slam '{selected_slam}'. Valid options: {', '.join(sorted(VALID_SLAM))}"
        )

    if selected_slam == 'slam_toolbox':
        try:
            get_package_share_directory('slam_toolbox')
        except PackageNotFoundError as exc:
            raise RuntimeError(
                "SLAM mode 'slam_toolbox' requires package 'slam_toolbox', but it is not available in the "
                "current environment. Install/build 'slam_toolbox', or launch with 'slam:=cartographer' "
                "instead."
            ) from exc

    world_path = os.path.join(pkg_share, 'world', VALID_WORLDS[selected_world])
    selected_map_path = _resolve_selected_map(pkg_share, selected_map)
    resolved_map_file = _resolve_map_output_prefix(pkg_share, map_file)
    resolved_spawn_x, resolved_spawn_y, resolved_spawn_z = _resolve_spawn_pose(
        selected_world, spawn_x, spawn_y, spawn_z
    )
    workspace_models_path = os.path.join(pkg_share, '..')
    controller_config_file = os.path.join(pkg_share, 'config', 'controllers.yaml')
    cartographer_config_dir = os.path.join(pkg_share, 'config')
    slam_toolbox_config_file = os.path.join(pkg_share, 'config', 'slam_toolbox.yaml')
    xacro_file = os.path.join(pkg_share, 'urdf', 'slam2robot.urdf')

    robot_desc = xacro.process_file(xacro_file).toxml().replace(
        '__CONTROLLER_CONFIG_FILE__',
        controller_config_file,
    )

    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[
            os.environ.get('GAZEBO_MODEL_PATH', ''),
            ':',
            workspace_models_path,
        ],
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {
                'robot_description': robot_desc,
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }
        ],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_path}.items(),
        condition=IfCondition(LaunchConfiguration('start_gazebo')),
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic',
            'robot_description',
            '-entity',
            'slam2robot',
            '-x',
            resolved_spawn_x,
            '-y',
            resolved_spawn_y,
            '-z',
            resolved_spawn_z,
        ],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '-c',
            '/controller_manager',
            '--param-file',
            controller_config_file,
        ],
        output='screen',
    )

    joint_position_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_position_controller',
            '-c',
            '/controller_manager',
            '--param-file',
            controller_config_file,
        ],
        output='screen',
    )

    gazebo_group = GroupAction(
        condition=IfCondition(LaunchConfiguration('start_gazebo')),
        actions=[
            gazebo,
            spawn_entity,
            RegisterEventHandler(
                OnProcessExit(
                    target_action=spawn_entity,
                    on_exit=[joint_state_broadcaster_spawner],
                )
            ),
            RegisterEventHandler(
                OnProcessExit(
                    target_action=joint_state_broadcaster_spawner,
                    on_exit=[joint_position_controller_spawner],
                )
            ),
        ],
    )

    slam_is_cartographer = PythonExpression(
        ["'", LaunchConfiguration('slam'), "' == 'cartographer'"]
    )
    slam_is_slam_toolbox = PythonExpression(
        ["'", LaunchConfiguration('slam'), "' == 'slam_toolbox'"]
    )
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
        condition=IfCondition(slam_is_cartographer),
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='occupancy_grid_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-resolution', '0.05', '-publish_period_sec', '1.0'],
        condition=IfCondition(slam_is_cartographer),
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_toolbox_config_file,
            {'use_sim_time': LaunchConfiguration('use_sim_time')},
        ],
        condition=IfCondition(slam_is_slam_toolbox),
    )

    reference_map_actions = []
    if selected_map_path is not None:
        reference_map_actions.extend(
            [
                LogInfo(msg=[f'Loading reference map: {selected_map_path}']),
                Node(
                    package='nav2_map_server',
                    executable='map_server',
                    name='reference_map_server',
                    output='screen',
                    parameters=[
                        {
                            'yaml_filename': selected_map_path,
                            'topic_name': 'selected_map',
                            'frame_id': 'map',
                            'use_sim_time': LaunchConfiguration('use_sim_time'),
                        }
                    ],
                ),
                Node(
                    package='nav2_lifecycle_manager',
                    executable='lifecycle_manager',
                    name='reference_map_lifecycle_manager',
                    output='screen',
                    parameters=[
                        {
                            'use_sim_time': LaunchConfiguration('use_sim_time'),
                            'autostart': True,
                            'node_names': ['reference_map_server'],
                        }
                    ],
                ),
            ]
        )

    save_map_log = LogInfo(
        msg=[f'Map autosave target: {resolved_map_file}'],
        condition=IfCondition(LaunchConfiguration('save_map')),
    )
    spawn_log = LogInfo(
        msg=[
            f'Spawning robot at x={resolved_spawn_x}, y={resolved_spawn_y}, z={resolved_spawn_z}'
        ]
    )

    save_map_node = Node(
        package='slam2robot',
        executable='map_autosaver',
        name='map_autosaver',
        output='screen',
        parameters=[
            {
                'map_topic': '/map',
                'map_file': resolved_map_file,
                'free_thresh': LaunchConfiguration('free_thresh'),
                'occupied_thresh': LaunchConfiguration('occupied_thresh'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }
        ],
        condition=IfCondition(LaunchConfiguration('save_map')),
    )

    world_log = LogInfo(msg=[f'Launching Gazebo world: {selected_world} -> {world_path}'])
    slam_log = LogInfo(msg=[f'Using SLAM algorithm: {selected_slam}'])
    slam_group = GroupAction(
        condition=IfCondition(LaunchConfiguration('start_slam')),
        actions=[
            cartographer_node,
            occupancy_grid_node,
            slam_toolbox_node,
        ],
    )

    return [
        set_gazebo_model_path,
        world_log,
        slam_log,
        spawn_log,
        robot_state_publisher,
        gazebo_group,
        slam_group,
        *reference_map_actions,
        save_map_log,
        save_map_node,
    ]


def generate_launch_description():
    pkg_share = get_package_share_directory('slam2robot')
    default_map_dir = os.path.join(pkg_share, 'map', 'slam_map')

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('start_gazebo', default_value='true'),
            DeclareLaunchArgument('start_slam', default_value='true'),
            DeclareLaunchArgument('save_map', default_value='true'),
            DeclareLaunchArgument('world', default_value='world_1'),
            DeclareLaunchArgument('slam', default_value='cartographer'),
            DeclareLaunchArgument('selected_map', default_value='none'),
            DeclareLaunchArgument('map_file', default_value=default_map_dir),
            DeclareLaunchArgument('free_thresh', default_value='0.25'),
            DeclareLaunchArgument('occupied_thresh', default_value='0.65'),
            DeclareLaunchArgument('spawn_x', default_value='auto'),
            DeclareLaunchArgument('spawn_y', default_value='auto'),
            DeclareLaunchArgument('spawn_z', default_value='auto'),
            OpaqueFunction(function=_launch_setup),
        ]
    )
