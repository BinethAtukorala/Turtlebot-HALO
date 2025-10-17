import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Int32
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
import time

class HumanRangeFinder(Node):
    def __init__(self):
        super().__init__('human_range_finder')
        self.laser_scan = None
        # Subscribe to horizontal error
        self.subscription = self.create_subscription(
            Float32,
            '/human/error_x',
            self.error_callback,
            10

        )

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE, # Or other appropriate durability
            history=HistoryPolicy.KEEP_LAST,
            depth=1 # Or other appropriate depth
        )

        self.scan_subscription = self.create_subscription(
            LaserScan,
            '/scan', # Compressed images to save bandwith
            self.laserscan_callback,
            qos_profile
        )
        # Publisher for distance messages
        self.distance_pub = self.create_publisher(Int32, '/human/distance', 10)

        self.get_logger().info("Human Range Finder Node Started")

    def publish_distance(self, distance):
        msg = Int32()
        msg.data = distance
        self.distance_pub.publish(msg)
        self.get_logger().info(f"Published human distance: {distance}")

    def error_callback(self, msg: Int32):
        error = msg.data
        # pixels are -300 to 300
        # degrees from lidar are -60 to 60

        if self.laser_scan is not None:
            quadrant_size_pixels= int(600/7)
            quadrant_size_degrees = int(120/7)
            error_quadrant = (error + 300) // quadrant_size_pixels
            quadrant_scan = self.laser_scan[error_quadrant*quadrant_size_degrees:(error_quadrant+1)*quadrant_size_degrees]
            distance = sum(quadrant_scan) / len(quadrant_scan)
            self.publish_distance(int(distance))
            
        else:
            self.get_logger().warn("No laser scan data available")

    def laserscan_callback(self, msg: LaserScan):
        # the front 120 degrees is index -60 to 60
        ranges = msg.ranges
        front_ranges = ranges[-60:] + ranges[:60]
        # Lidar scan goes from robots left to right, -60 to 60 respectively
        # We want it to go from right to left to match the pixel error so we reverse the list
        front_ranges.reverse()
        self.laser_scan = front_ranges

def main(args=None):
    rclpy.init(args=args)
    node = HumanRangeFinder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
