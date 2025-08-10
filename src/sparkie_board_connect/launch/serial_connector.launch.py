from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Dichiarazione degli argomenti del launch file
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyUSB0',
        description='Porta seriale da utilizzare'
    )
    
    baud_rate_arg = DeclareLaunchArgument(
        'baud_rate',
        default_value='115200',
        description='Baud rate della connessione seriale'
    )
    
    timeout_arg = DeclareLaunchArgument(
        'timeout',
        default_value='1.0',
        description='Timeout della connessione seriale in secondi'
    )
    
    # Nodo principale di connessione seriale
    serial_node = Node(
        package='sparkie_board_connect',
        executable='serial_node',
        name='serial_connector_node',
        parameters=[{
            'serial_port': LaunchConfiguration('serial_port'),
            'baud_rate': LaunchConfiguration('baud_rate'),
            'timeout': LaunchConfiguration('timeout'),
        }],
        output='screen'
    )
    
    return LaunchDescription([
        serial_port_arg,
        baud_rate_arg,
        timeout_arg,
        serial_node
    ])
