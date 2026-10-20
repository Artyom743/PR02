import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro  # <--- ОБЯЗАТЕЛЬНО ДОБАВИТЬ ИМПОРТ


def generate_launch_description():
    pkg_path = get_package_share_directory('course_description')

    # Путь к файлу Xacro
    xacro_file = os.path.join(pkg_path, 'urdf', 'vehicle.urdf.xacro')

    # МАГИЯ ЗДЕСЬ: Парсим Xacro в строку URDF
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description = {'robot_description': doc.toxml()}

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[robot_description],
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_path, 'rviz', 'config.rviz')]
        )
    ])
