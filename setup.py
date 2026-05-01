from setuptools import setup
import os
from glob import glob

package_name = 'slam2robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'world'), glob('world/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Phuc',
    maintainer_email='dvanphuc2005@gmail.com',
    description='Robot Simulation with ROS2 Camera and IMU',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'arm_controller = slam2robot.arm_controller:main',
        ],
    },
)
