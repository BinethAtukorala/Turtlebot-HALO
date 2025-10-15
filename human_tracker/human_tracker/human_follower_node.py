import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import random
from ultralytics import YOLO
import numpy as np
from time import sleep

class HumanFollowerNode(Node):
    def __init__(self):
        super().__init__('human_follower_node')

        self.kP = 1.0
        self.kD = 0.0
        self.kI = 0.0

        # Subscribe to horizontal error
        self.subscription = self.create_subscription(
            Int32,
            '/human_error_x', # Compressed images to save bandwith
            self.error_callback,
            10
        )

        # cmd_vel publisher
        self.cmdvel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )



    def error_callback(self, msg: Int32):
        error = msg.data

        vel = Twist()

        vel.angular.z = -0.5 * error/256

        self.cmdvel_publisher.publish(vel)



def main(args=None):import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import random
from ultralytics import YOLO
import numpy as np

class HumanFollowerNode(Node):
    def __init__(self):
        super().__init__('human_follower_node')

        self.kP = 1.0
        self.kD = 0.0
        self.kI = 0.0

        # Subscribe to horizontal error
        self.subscription = self.create_subscription(
            Int32,
            '/human_error_x', # Compressed images to save bandwith
            self.error_callback,
            10
        )

        # cmd_vel publisher
        self.cmdvel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )



    def error_callback(self, msg: Int32):
        error = msg.data

        vel = Twist()

        vel.angular.z = -0.5 * error/256

        self.cmdvel_publisher.publish(vel)



def main(args=None):
    rclpy.init(args=args)
    node = HumanFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

    rclpy.init(args=args)
    node = HumanFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        twist = Twist()
        
        twist.linear.x = 0
        twist.linear.y = 0
        twist.angular.z = 0


        node.cmdvel_publisher.publish(twist)
        sleep(0.5)

        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
