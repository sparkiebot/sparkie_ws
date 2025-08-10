import os
import pathlib
import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.substitutions.path_join_substitution import PathJoinSubstitution
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from webots_ros2_driver.webots_launcher import WebotsLauncher
from webots_ros2_driver.webots_controller import WebotsController

def generate_launch_description():
    world = LaunchConfiguration('world')
    package_dir = get_package_share_directory("sparkie_sim")

    desc_package_dir = get_package_share_directory("sparkie_description")
    urdf_path = os.path.join(desc_package_dir, 'urdf', 'sparkiebot.xacro')
    robot_description = pathlib.Path(urdf_path).read_text()

    # Include the launch file that starts the robot's description

    desc_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(desc_package_dir, 'launch', 'desc.launch.py')
        )
    )




    # Define your URDF robots here
    # The name of an URDF robot has to match the WEBOTS_CONTROLLER_URL of the driver node
    # You can specify the URDF file to use with "urdf_path"
    

    # Driver nodes
    # When having multiple robot it is enough to specify the `additional_env` argument.
    # The `WEBOTS_CONTROLLER_URL` has to match the robot name in the world file.
    # You can check for more information at:
    # https://cyberbotics.com/doc/guide/running-extern-robot-controllers#single-simulation-and-multiple-extern-robot-controllers
    robot_driver = Node(
        package='webots_ros2_driver',
        executable='driver',
        output='screen',
        additional_env={'WEBOTS_CONTROLLER_URL': 'sparkie'},
        parameters=[
            {'robot_description': robot_description},
        ],
    )

    # The WebotsLauncher is a Webots custom action that allows you to start a Webots simulation instance.
    # It searches for the Webots installation in the path specified by the `WEBOTS_HOME` environment variable and default installation paths.
    # The Ros2Supervisor node is mandatory to spawn an URDF robot.
    # The accepted arguments are:
    # - `world` (str): Path to the world to launch.
    # - `gui` (bool): Whether to display GUI or not.
    # - `mode` (str): Can be `pause`, `realtime`, or `fast`.
    # - `ros2_supervisor` (bool): Spawn the `Ros2Supervisor` custom node that communicates with a Supervisor robot in the simulation.
    webots = WebotsLauncher(
        world=PathJoinSubstitution([package_dir, 'worlds', world]),
        ros2_supervisor=True
    )

    sparkie_controller = WebotsController(
        robot_name='sparkiebot',
        parameters=[
            {'robot_description': urdf_path,
             'use_sim_time': True,
             'set_robot_state_publisher': True},
            
        ],
        #remappings=mappings,
        respawn=True
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value='apartment.wbt',
            description='Choose one of the world files from `/webots_ros2_universal_robot/worlds` directory'
        ),

        # Include the launch file that starts the robot's description
        desc_launch,

        # Starts Webots
        webots,

        # Starts the Ros2Supervisor node created with the WebotsLauncher
        webots._supervisor,

        # Starts the driver node
        sparkie_controller,

        # This action will kill all nodes once the Webots simulation has exited
        launch.actions.RegisterEventHandler(
            event_handler=launch.event_handlers.OnProcessExit(
                target_action=webots,
                on_exit=[launch.actions.EmitEvent(event=launch.events.Shutdown())],
            )
        )
    ])