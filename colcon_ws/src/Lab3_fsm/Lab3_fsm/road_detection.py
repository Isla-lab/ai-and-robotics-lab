#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
import torch
from ultralytics import YOLO


class TrafficSignDetector(Node):

    def __init__(self):
        super().__init__('traffic_sign_detector')

        # --- ROS PUBLISHERS ---
        self.sign_pub = self.create_publisher(String, '/traffic_sign', 10)  # Publish detected traffic signs
        self.image_pub = self.create_publisher(Image, '/yolo/visual_debug', 10)  # Publish annotated debug image

        # --- ROS SUBSCRIBER ---
        # Subscribe to camera feed, queue=1 to avoid lag
        self.subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            1
        )

        # CV bridge for ROS ↔ OpenCV conversion
        self.bridge = CvBridge()
        self.latest_frame = None  # Store most recent camera frame

        # --- LOAD YOLO MODEL ---
        self.get_logger().info("Loading YOLO model...")
        self.model = #TODO

        # Check hardware
        if torch.cuda.is_available():
            self.get_logger().info("Using CUDA")
        else:
            self.get_logger().info("Using CPU")

        # --- DETECTION PARAMETERS ---
        self.conf_threshold = 0.4  # Minimum confidence for valid detection
        self.imgsz = 320            # YOLO internal resize (optimized for speed)

        # --- PERIODIC INFERENCE TIMER ---
        self.timer = self.create_timer(0.1, self.run_inference)  # Run at 10 Hz

        self.get_logger().info("Traffic Sign Detector ready (optimized for 256px frames).")

    # ---------------------------------
    # ROS IMAGE CALLBACK
    # Store the latest camera frame for inference
    # ---------------------------------
    def image_callback(self, msg):
        try:
            # Convert ROS Image to OpenCV RGB
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, "rgb8")
        except Exception as e:
            self.get_logger().error(f"CvBridge error: {str(e)}")

    # ---------------------------------
    # INFERENCE LOOP (runs at 10 Hz)
    # Performs YOLO detection on the latest frame
    # ---------------------------------
    def run_inference(self):

        if self.latest_frame is None:
            return  # Skip if no frame available

        # Copy frame to avoid overwriting
        frame = self.latest_frame.copy()

        # Convert RGB → BGR for OpenCV drawing
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        try:
            # Run YOLO detection
            results = self.model.predict(
                frame,
                imgsz=self.imgsz,
                conf=self.conf_threshold,
                verbose=False
            )

            annotated_frame = frame.copy()
            best_sign = None
            best_conf = 0.0

            # Iterate over detected boxes
            for result in results:

                if result.boxes is None:
                    continue

                for box in result.boxes:

                    # Extract bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id]

                    # Draw bounding box
                    cv2.rectangle(
                        annotated_frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    # Draw label with class name and confidence
                    label = f"{class_name} {conf:.2f}"
                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

                    # Track the detection with highest confidence
                    if conf > best_conf:
                        best_conf = conf
                        best_sign = class_name

            # --- PUBLISH BEST SIGN ---
            if best_sign is not None:
                msg = String()
                msg.data = best_sign
                self.sign_pub.publish(msg)
                self.get_logger().info(f"Detected: {best_sign} ({best_conf:.2f})")

            # --- PUBLISH DEBUG IMAGE ---
            img_msg = self.bridge.cv2_to_imgmsg(annotated_frame, "bgr8")
            self.image_pub.publish(img_msg)

        except Exception as e:
            self.get_logger().error(f"Inference error: {str(e)}")


def main(args=None):
    rclpy.init(args=args)
    node = TrafficSignDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()