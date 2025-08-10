from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sparkie_board_connect'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pyserial', 'protobuf'],
    zip_safe=True,
    maintainer='mattsays',
    maintainer_email='mattsays@sparkie.com',
    description='Bridge between Sparkie board and ROS2 ',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sparkie_board = sparkie_board_connect.sparkie_board:main',
        ],
    },
)
