#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from std_msgs.msg import String
import serial
import threading
import argparse
import sys


class SparkieBoardNode(Node):
    """
    ROS2 node for serial communication with an external board/device.
    Publishes data received from the serial port and allows sending commands.
    """
    
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=115200):
        super().__init__('board', namespace='sparkie')

        # Node parameters
        self.declare_parameter('serial_port', serial_port)
        self.declare_parameter('baud_rate', baud_rate)
        self.declare_parameter('timeout', 1.0)
        
        # Get parameters
        self.serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
        self.baud_rate = self.get_parameter('baud_rate').get_parameter_value().integer_value
        self.timeout = self.get_parameter('timeout').get_parameter_value().double_value
        
        
        # Initialize serial connection
        self.serial_connection = None
        self.is_connected = False
        self.reading_thread = None
        self.should_stop = False
        
        # Connect to serial port
        self.connect_to_serial()
        
        # Information logs
        self.get_logger().info(f'SerialConnector node started')
        self.get_logger().info(f'Serial port: {self.serial_port}')
        self.get_logger().info(f'Baud rate: {self.baud_rate}')
        self.get_logger().info(f'Timeout: {self.timeout}s')
    
    def connect_to_serial(self):
        """Establishes connection with the serial port"""
        try:
            self.serial_connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            if self.serial_connection.is_open:
                self.is_connected = True
                self.get_logger().info(f'Successfully connected to port {self.serial_port}')
                
                # Start the thread for continuous reading
                self.start_reading_thread()
            else:
                self.get_logger().error(f'Unable to open port {self.serial_port}')
                
        except serial.SerialException as e:
            self.get_logger().error(f'Serial connection error: {e}')
            self.is_connected = False
        except Exception as e:
            self.get_logger().error(f'Unexpected error: {e}')
            self.is_connected = False
    
    def start_reading_thread(self):
        """Starts the thread for continuous reading from serial port"""
        if self.is_connected and self.reading_thread is None:
            self.reading_thread = threading.Thread(target=self.read_serial_data)
            self.reading_thread.daemon = True
            self.should_stop = False
            self.reading_thread.start()
            self.get_logger().info('Serial reading thread started')
    
    def read_serial_data(self):
        """Continuously reads data from the serial port"""
        while not self.should_stop and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    # Read a line from serial
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    
                    if data:
                        # Publish received data
                        msg = String()
                        msg.data = data
                        self.data_publisher.publish(msg)
                        
                        self.get_logger().debug(f'Data received: {data}')
                        
            except serial.SerialException as e:
                self.get_logger().error(f'Serial reading error: {e}')
                self.reconnect()
                break
            except UnicodeDecodeError as e:
                self.get_logger().warning(f'Decoding error: {e}')
            except Exception as e:
                self.get_logger().error(f'Unexpected reading error: {e}')
                break
    
    def send_command_callback(self, msg):
        """Callback to send commands to the serial port"""
        if self.is_connected and self.serial_connection:
            try:
                # Add line terminator if not present
                command = msg.data
                if not command.endswith('\n'):
                    command += '\n'
                
                # Send the command
                self.serial_connection.write(command.encode('utf-8'))
                self.serial_connection.flush()
                
                self.get_logger().info(f'Command sent: {msg.data}')
                
            except serial.SerialException as e:
                self.get_logger().error(f'Command sending error: {e}')
                self.reconnect()
            except Exception as e:
                self.get_logger().error(f'Unexpected sending error: {e}')
        else:
            self.get_logger().warning('Serial connection not available for command sending')
    
    def reconnect(self):
        """Attempts to reconnect to the serial port"""
        self.get_logger().info('Reconnection attempt...')
        self.disconnect()
        
        # Wait a moment before reconnecting
        import time
        time.sleep(2)
        
        self.connect_to_serial()
    
    def disconnect(self):
        """Disconnects from the serial port"""
        self.should_stop = True
        self.is_connected = False
        
        if self.reading_thread:
            self.reading_thread.join(timeout=2)
            self.reading_thread = None
        
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.get_logger().info('Serial connection closed')
    
    def destroy_node(self):
        """Cleanup when the node is destroyed"""
        self.disconnect()
        super().destroy_node()


def main(args=None):
    # Command line arguments parsing
    parser = argparse.ArgumentParser(description='ROS2 node for serial connection')
    parser.add_argument('--serial-port', default='/dev/ttyUSB0',
                       help='Serial port to use (default: /dev/ttyUSB0)')
    parser.add_argument('--baud-rate', type=int, default=115200,
                       help='Serial connection baud rate (default: 115200)')
    
    # Parse only known arguments to avoid conflicts with ROS2
    known_args, remaining_args = parser.parse_known_args()
    
    # Initialize ROS2
    rclpy.init(args=remaining_args)
    
    try:
        # Create the node with specified parameters
        node = SparkieBoardNode(
            serial_port=known_args.serial_port,
            baud_rate=known_args.baud_rate
        )
        
        # Spin the node
        rclpy.spin(node)
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error in node execution: {e}')
    finally:
        # Cleanup
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
