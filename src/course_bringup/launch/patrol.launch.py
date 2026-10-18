from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ns = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    sub_rel = LaunchConfiguration('subscriber_reliability')

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument('subscriber_reliability', default_value='reliable'),

        # turtlesim глобально
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),

        # patrol в namespace, cmd_vel -> /turtle1/cmd_vel
        Node(
            package='patrol', executable='patrol',
            namespace=ns,
            remappings=[('cmd_vel', '/turtle1/cmd_vel')],
            output='screen',
        ),

        # pose_relay в namespace
        Node(
            package='patrol', executable='pose_relay',
            namespace=ns,
            output='screen',
        ),

        # Запись только при record:=true
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-s', 'mcap',
                 '-o', bag_dir,
                 ['/', ns, '/sensor_pose']],
            condition=IfCondition(record),
            output='screen',
        ),
    ])