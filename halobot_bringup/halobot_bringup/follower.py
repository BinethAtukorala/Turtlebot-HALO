import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist

from halobot_msgs.srv import PidParam

import cv2
from cv_bridge import CvBridge
from ultralytics import YOLO
import numpy as np

from time import sleep
import random
import sys
import threading

class HumanFollowerNode(Node):
    def __init__(self):
        super().__init__('human_follower_node')

        # Parameterse read
        self.declare_parameter('max_linear_speed', 1)
        self.declare_parameter('max_angular_speed', 1.5)
        self.declare_parameter('kP', 0.3)
        self.declare_parameter('kD', 0.0)
        self.declare_parameter('kI', 0.0)
        self.declare_parameter('kAng', 0.1)

        # Load params

        self.max_linear_speed = float(self.get_parameter('max_linear_speed').value)
        self.max_angular_speed = float(self.get_parameter('max_angular_speed').value)

        self.kP = float(self.get_parameter('kP').value)
        self.kD = float(self.get_parameter('kD').value)
        self.kI = float(self.get_parameter('kI').value)
        self.kAng = float(self.get_parameter('kAng').value)

        # Local variables for PID

        self.previous_time = None
        self.previous_error = 0
        self.cumulative_error = 0

        ## Subscribers    

        # Horizontal error
        self.error_subscription = self.create_subscription(
            Int32,
            '/human/error_x', # Compressed images to save bandwith
            self.error_callback,
            10
        )   

        ## Publishers

        # cmd_vel publisher
        self.cmdvel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        ## Services

        # PID params updater
        self.pid_service = self.create_service(
            PidParam, 
            '/pid', 
            self.pid_callback
        )

        self.get_logger().info("Human Follower Node Started")



    def error_callback(self, msg: Int32):
        # Skip first error reading to get an accurate time delta 
        if type(self.previous_time) == type(None):
            self.previous_time = self.get_clock().now()
            pass

        error = msg.data

        vel = Twist()

        now_time = self.get_clock().now()

        delta_time = (now_time - self.previous_time).nanoseconds / pow(10, 6)

        # PID Control
        self.cumulative_error += error * delta_time
        rate_error = (error - self.previous_error)/delta_time

        output = (self.kP * error) + (self.kI * self.cumulative_error) + (self.kD * rate_error)
        
        
        vel.angular.z = float(np.clip(
            -self.kAng * output, 
            -self.max_angular_speed, self.max_angular_speed
            ))
        
        # The higher abs(output) is, steering should decrease
        vel.linear.x = float(np.clip(
            self.max_linear_speed * (1 - min(abs(output)/100, 1)),
            0,
            self.max_linear_speed
            ))

        self.previous_error = error
        self.previous_time = now_time
        self.cmdvel_publisher.publish(vel)
        self.get_logger().info(f"Output: {output} Lin: {vel.linear.x} Ang: {vel.angular.z}")

    def pid_callback(self, request, response):
        self.kP += request.kp_i
        self.kI += request.ki_i
        self.kD += request.kd_i
        self.kAng += request.kang_i

        response.kp = self.kP
        response.ki = self.kI
        response.kd = self.kD
        response.kang = self.kAng

        self.get_logger().info(f"Updated PID: {self.kP} {self.kD} {self.kI} : {self.kAng}")

        return response
        
        


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
