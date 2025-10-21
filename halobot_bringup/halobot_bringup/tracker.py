import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from std_msgs.msg import Int32, Bool
from cv_bridge import CvBridge
import cv2
import random
from ultralytics import YOLO
import numpy as np

import os
from ament_index_python.packages import get_package_share_directory

class HumanTrackerNode(Node):
    def __init__(self):
        super().__init__('human_tracker_node')

        super().__init__('human_range_finder')

        self.declare_parameter('sim', False)

        self.sim = self.get_parameter('sim').value

        # Subscribe to camera images
        self.subscription = self.create_subscription(
            Image if self.sim else CompressedImage,
            '/camera/image_raw' if self.sim else '/image_raw/compressed', # Compressed images to save bandwith
            self.image_callback,
            10
        )

        # Horizontal error publisher
        self.error_publisher = self.create_publisher(
            Int32, 
            '/human/error_x', 
            10
        )

        # Detection status publisher
        self.detected_publisher = self.create_publisher(
            Bool, 
            '/human/detected', 
            10
        )

        self.bridge = CvBridge()

        pkg_share_dir = get_package_share_directory('halobot_bringup')
        data_file = os.path.join(pkg_share_dir, 'models', 'yolo11s.pt')

        self.yolo = YOLO(data_file)
        self.yolo.classes = [0]
        self.get_logger().info("Human Tracker Node Started")

    def get_colours(self, cls_num):
        random.seed(cls_num)
        return tuple(random.randint(0, 255) for _ in range(3))

    def image_callback(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)

        frame = None

        if(type(msg) == CompressedImage):
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        elif(type(msg) == Image):
            frame = np_arr.reshape((msg.height, msg.width, 3)) 
        
        height, width, _ = frame.shape
        frame_center_x = width // 2

        horizontal_error = None

        # Run YOLO tracking
        results = self.yolo.track(frame, stream=True, verbose=False)

        for result in results:
            class_names = result.names
            for box in result.boxes:
                if box.conf[0] > 0.4:
                    cls = int(box.cls[0])
                    class_name = class_names[cls]

                    # Only detect humans
                    if class_name != "person":
                        continue

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    colour = self.get_colours(cls)

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
                    cv2.putText(frame, f"{class_name} {conf:.2f}",
                                (x1, max(y1 - 10, 20)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, colour, 2)

                    # Compute horizontal error (from center)
                    human_center_x = (x1 + x2) // 2
                    horizontal_error = human_center_x - frame_center_x

                    # Display error on image
                    cv2.putText(frame, f"Error X: {horizontal_error}",
                                (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1.0, (0, 0, 255), 2)

        # Publish horizontal error if a human is detected
        if horizontal_error is not None:
            error_msg = Int32()
            error_msg.data = horizontal_error
            self.error_publisher.publish(error_msg)
            
            bool_msg = Bool()
            bool_msg.data = True
            self.detected_publisher.publish(bool_msg)
            self.get_logger().info(f"Human detected. Error: {horizontal_error}")
        else:
            bool_msg = Bool()
            bool_msg.data = False
            self.detected_publisher.publish(bool_msg)
            self.get_logger().info(f"Human not detected")

        # Show processed image
        cv2.imshow("Human Tracker", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = HumanTrackerNode()
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
