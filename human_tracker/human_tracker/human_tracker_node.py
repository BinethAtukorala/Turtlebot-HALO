import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import Int32
from cv_bridge import CvBridge
import cv2
import random
from ultralytics import YOLO
import numpy as np

class HumanTrackerNode(Node):
    def __init__(self):
        super().__init__('human_tracker_node')

        # Subscribe to camera images
        self.subscription = self.create_subscription(
            CompressedImage,
            '/image_raw/compressed', # Compressed images to save bandwith
            self.image_callback,
            10
        )

        # Horizontal error publisher
        self.error_publisher = self.create_publisher(Int32, '/human/error_x', 10)

        self.bridge = CvBridge()
        self.yolo = YOLO("yolov8s.pt")
        self.get_logger().info("Human Tracker Node Started")

    def get_colours(self, cls_num):
        random.seed(cls_num)
        return tuple(random.randint(0, 255) for _ in range(3))

    def image_callback(self, msg: CompressedImage):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        height, width, _ = frame.shape
        frame_center_x = width // 2

        horizontal_error = None

        # Run YOLO tracking
        results = self.yolo.track(frame, stream=True)

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
            msg_error = Int32()
            msg_error.data = horizontal_error
            self.error_publisher.publish(msg_error)
            self.get_logger().info(f"Published horizontal error: {horizontal_error}")

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
