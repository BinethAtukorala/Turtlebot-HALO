import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from geometry_msgs.msg import Twist
import time

class HumanFollowerNode(Node):
    def __init__(self):
        super().__init__('human_follower_node')

        # Subscribe to horizontal error
        self.subscription = self.create_subscription(
            Int32,
            '/human/error_x',
            self.error_callback,
            10
        )

        # Publisher to TurtleBot3 cmd_vel
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # PID parameters
        self.Kp = 0.002      # Proportional gain
        self.Ki = 0.0        # Integral gain
        self.Kd = 0.001      # Derivative gain

        # PID variables
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_time = time.time()

        # Max angular speed
        self.max_angular = 0.5

        # Forward speed (constant)
        self.forward_speed = 0.1

        self.get_logger().info("Human Follower Node Started")

    def error_callback(self, msg: Int32):
        error = msg.data

        # Compute time difference
        current_time = time.time()
        dt = current_time - self.prev_time if self.prev_time else 0.01

        # PID calculations
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt

        angular_z = self.Kp * error + self.Ki * self.integral + self.Kd * derivative

        # Clamp angular speed
        angular_z = max(min(angular_z, self.max_angular), -self.max_angular)

        # Publish cmd_vel
        twist = Twist()
        twist.linear.x = self.forward_speed
        twist.angular.z = angular_z
        self.cmd_pub.publish(twist)

        # Save for next iteration
        self.prev_error = error
        self.prev_time = current_time

        self.get_logger().info(f"Error: {error}, Angular z: {angular_z:.3f}")


def main(args=None):
    rclpy.init(args=args)
    node = HumanFollowerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot on shutdown
        twist = Twist()
        node.cmd_pub.publish(twist)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
