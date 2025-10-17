from setuptools import find_packages, setup
import os, glob

package_name = 'halobot_bringup'

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
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            f'tracker = {package_name}.tracker:main',
            f'follower = {package_name}.follower:main',
            f'range_finder = {package_name}.range_finder:main'
        ],
    },
)
