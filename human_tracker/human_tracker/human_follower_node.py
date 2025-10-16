import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, LaserScan
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import random
from ultralytics import YOLO
import numpy as np
from time import sleep

import threading

class HumanFollowerNode(Node):
    def __init__(self):
        super().__init__('human_follower_node')

        self.kP = 1.0
        self.kD = 0.0
        self.kI = 0.0

        self.laser_scan = None
        self.scan_lock = threading.Lock()
    

        # Subscribe to horizontal error
        self.error_subscription = self.create_subscription(
            Int32,
            '/human_error_x', # Compressed images to save bandwith
            self.error_callback,
            10
        )   

        # Subscribe to lidar scan
        self.lidar_subscription = self.create_subscription(
            LaserScan,
            '/scan', 
            self.scan_callback,
            5
        )

        # cmd_vel publisher
        self.cmdvel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )



    def error_callback(self, msg: Int32):
        error = msg.data

        if(abs(error) > 10):

            vel = Twist()

            vel.angular.z = -0.75 * error/256
            vel.linear.x = 0.0

            self.cmdvel_publisher.publish(vel)
        
        else:
            scan = None
            with self.scan_lock:
                scan = self.laser_scan
            
            print(scan)

            vel = Twist()

            vel.linear.x = 0.15
            vel.angular.z = 0.0

            
            self.cmdvel_publisher.publish(vel)

        # vel = Twist()

    def scan_callback(self, msg: LaserScan):
        with self.scan_lock:
            self.laser_scan = msg


def main(args=None):
    rclpy.init(args=args)
    node = HumanFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        twist = Twist()
        
        # twist.linear.x = 0
        # twist.angular.z = 0

        node.cmdvel_publisher.publish(twist)
        sleep(0.5)

        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
