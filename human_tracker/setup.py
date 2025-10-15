from setuptools import find_packages, setup
import os, glob

package_name = 'human_tracker'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'models'), ['models/yolo11n.pt'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bineth',
    maintainer_email='bineth.mandiv@gmail.com',
    description='Human tracker node using YOLO',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'human_tracker_node = human_tracker.human_tracker_node:main',
            'human_follower_node = human_tracker.human_follower_node:main'
        ],
    },
)
