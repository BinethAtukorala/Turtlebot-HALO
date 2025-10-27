#!/usr/bin/env python3
import math
from typing import List, Tuple
import numpy as np
from threading import Lock
import os

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

from std_msgs.msg import Int32MultiArray, Bool, Float32, Int32
from sensor_msgs.msg import LaserScan



class RangeFinder(Node):

    def __init__(self):
        super().__init__('range_finder')

        # Image parameters
        self.declare_parameter('img_width', 600)
        self.declare_parameter('no_of_sectors', 5)
        self.declare_parameter('front_arc', 90)

        self.img_width = int(self.get_parameter('img_width').value)
        self.no_of_sectors = int(self.get_parameter('no_of_sectors').value)
        self.front_arc = int(self.get_parameter('front_arc').value)

        # Mutex locks 
        self.last_errors = []
        self.have_error = False

        self.scan_lock = Lock()
        self.latest_scan = None
        
        # Sensor quality of service information
        # The Turtlebot3 can only provide under Best Effort reliability
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        ## Subscriptions

        # Humans detected
        self.create_subscription(
            Int32MultiArray, 
            '/human/error_x', 
            self.error_callback, 
            10
        )
        
        # Laser scan data
        self.create_subscription(
            LaserScan, 
            '/scan', 
            self.scan_callback, 
            sensor_qos
        )

        ## Publishers

        # Distance to the selected target
        self.dist_pub = self.create_publisher(Float32, '/human/closest_distance', 10)

        # Selected target
        self.at_target_pub = self.create_publisher(Int32, '/human/at_target', 10)

        self.get_logger().info('Range Finder Node Started')

    def error_callback(self, msg: Int32MultiArray):
        # store latest image error (in pixels, signed)
        self.last_errors = msg.data
        
        # Get laser scan data
        laser_scan = None
        with self.scan_lock:
            laser_scan = self.latest_scan
        
        if laser_scan is not None:
            # print(laser_scan.ranges)
            # print("------------------------------")
            min_distance = math.inf
            target_x = None

            # Iterate through reported humans and find closest
            for error in self.last_errors:

                # Calculate size of linear and angular sections
                section_size = self.img_width/self.no_of_sectors
                section_degrees = self.front_arc/self.no_of_sectors

                # Calculate which linear section the human is in
                error_section = (np.clip((error + self.img_width/2) // section_size, 0, 4))-2

                valid_ranges_in_section = []

                # Calculate angular section the human is in
                starting_theta = int((error_section * math.radians(section_degrees)+math.radians(90)) / laser_scan.angle_increment)
                ending_theta = int(starting_theta + math.radians(section_degrees) / laser_scan.angle_increment)

                # Get sum of valid ranges in the selected angular section
                for detected_range in laser_scan.ranges[-30:]:
                    if detected_range > laser_scan.range_min and detected_range < laser_scan.range_max:
                        valid_ranges_in_section.append(detected_range)
                
                # Skip if no valid ranges are found
                if(len(valid_ranges_in_section) == 0):
                    # self.get_logger().warn("No valid range found. Skipping...")
                    return

                # Get the average of range values
                average_range_in_section = sum(valid_ranges_in_section)/len(valid_ranges_in_section)

                self.get_logger().debug(f"Quadrant: {error_section} Range: {average_range_in_section}")

                # Update minimum distance and target selected
                if average_range_in_section < min_distance:
                    min_distance = average_range_in_section
                    target_x = error

            # Publish selected target
            if(target_x != None):
                dist_msg = Float32()
                if target_x < 50 and target_x > -50:
                    dist_msg.data = min_distance
                else:
                    dist_msg.data = 2000.0
                
                self.dist_pub.publish(dist_msg)

                tgt_msg = Int32()
                tgt_msg.data = target_x

                self.at_target_pub.publish(tgt_msg)

                self.get_logger().info(f"Target: {target_x}  Distance: {dist_msg}")
            
            # Publish placeholder values if no human is found
            # This will have the robot search for humans
            else:
                dist_msg = Float32()
                dist_msg.data = math.inf
                
                self.dist_pub.publish(dist_msg)

                tgt_msg = Int32()
                tgt_msg.data = 5000
                self.at_target_pub.publish(tgt_msg)



        else:
            self.get_logger().warn("No laser scan available")

            # Publish placeholder values if no human is found
            # This will have the robot search for humans

            dist_msg = Float32()
            dist_msg.data = math.inf
            
            self.dist_pub.publish(dist_msg)

            tgt_msg = Int32()
            tgt_msg.data = 5000
            self.at_target_pub.publish(tgt_msg)

       
    # Store laser scan data
    def scan_callback(self, msg: LaserScan):
        with self.scan_lock:
            self.latest_scan = msg


    

def main(args=None):
    rclpy.init(args=args)
    node = RangeFinder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
