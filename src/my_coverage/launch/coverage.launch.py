import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory('oomwoo_gazebo'),
                     'launch', 'world.launch.py')))

    nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('oomwoo_bringup'),
                         'launch', 'navigation.launch.py')),
        launch_arguments={'use_sim_time': 'true', 'slam': 'True'}.items())

    coverage = Node(package='my_coverage', executable='coverage',
                    name='coverage', parameters=[{'use_sim_time': True}])

    # give Gazebo + SLAM ~12 s to come up before the robot starts moving
    return LaunchDescription([gazebo, nav, TimerAction(period=12.0, actions=[coverage])])
