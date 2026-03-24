#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

import cv2
import math
import numpy as np
import time

from ultralytics import YOLO

class OrangeFollower(Node):

    def __init__(self):
        super().__init__('orange_follower')

        # -------- YOLO --------
        self.target_class = "orange"
        self.conf_threshold = 0.25

        # -------- DISTANCE CONTROL --------
        self.desired_distance = 0.8       
        self.dist_tolerance = 0.12      
        self.k_linear = 0.5              

        # -------- ANGULAR CONTROL e^2 --------
        self.k_yaw = 0.003
        self.max_linear_speed = 0.35
        self.max_angular_speed = 1.0

        # -------- MEMORY / HOLDING --------
        self.last_twist = Twist()
        self.last_detection_time = 0.0
        self.cmd_hold_time = 0.3         

        # -------- SEARCH MODE --------
        self.search_time_threshold = 2.0  
        self.search_angular_speed = 0.3   

        # -------- DEPTH --------
        self.depth_frame = None
        self.last_distance = self.desired_distance

        # -------- ROS --------
        self.sub_img = self.create_subscription(
            Image, '/camera/color/image_raw', self.image_callback, 10)
        self.sub_depth = self.create_subscription(
            Image, '/camera/depth/image_raw', self.depth_callback, 10)

        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_debug = self.create_publisher(
            Image, '/yolo/debug_image', 10)

        # -------- YOLO MODEL --------
        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")

        self.get_logger().info("Orange follower started")

    # -----------------------------
    # DEPTH CALLBACK
    # -----------------------------
    def depth_callback(self, msg):
        try:
            self.depth_frame = self.bridge.imgmsg_to_cv2(msg, "32FC1")
        except Exception as e:
            self.get_logger().error(f"Depth conversion error: {e}")

    # -----------------------------
    # IMAGE CALLBACK
    # -----------------------------
    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            if frame is None or frame.mean() < 5:
                return
        except Exception as e:
            self.get_logger().error(f"CV Bridge error: {e}")
            return

        h, w, _ = frame.shape
        center_x = w // 2

        results = self.model.predict(frame, conf=self.conf_threshold, verbose=False)

        best_target = None
        best_conf = 0.0
        max_area = 0

        # -------- Find best orange --------
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                conf = float(box.conf[0])

                # TODO: EXERCISE 1 - Find the largest target
                # Select the best detection corresponding to the target class.
                # 
                # Suggested strategy:
                #   1. Check if the detected class (cls_name) matches self.target_class.
                #   2. Extract the bounding box coordinates.
                #      (Hint: x1, y1, x2, y2 = map(int, box.xyxy[0]))
                #   3. Compute the area of the bounding box.
                #   4. If this area is greater than 'max_area':
                #      - Update 'max_area' with the current area.
                #      - Save the coordinates in 'best_target' as a tuple: (x1, y1, x2, y2).
                #      - Update 'best_conf' with the current confidence score (conf).
                

        twist = Twist()
        target_found = False

        # -----------------------------
        # TARGET FOUND
        # -----------------------------
        if best_target and self.depth_frame is not None:
            x1, y1, x2, y2 = best_target
            # TODO:
            # Compute the centre (cx, cy) of the bounding box.
            # --- Add your code here ---
            # cx = ...
            # cy = ...

            # draw bbox and centre
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,165,255), 3)
            cv2.circle(frame, (cx, cy), 5, (0,255,0), -1)

            # depth from centre
            try:
                # TODO: EXERCISE 3 - Depth estimation
                # Estimate the object distance using the depth image.
                # 
                # Suggested strategy:
                #   - Extract a small window (e.g., 5x5 pixels) around (cx, cy) from 'self.depth_frame'.
                #     (Hint: Remember that numpy arrays are indexed as [rows, cols], so use [y, x]!)
                #   - Compute the mean depth value of this window.
                #   - Ignore NaN values (Hint: look at numpy's nanmean function).
                
                
                # --- Add your code here ---
                # window = ...
                # distance = ...

                distance = None
                if math.isnan(distance) or distance <= 0:
                    distance = self.last_distance
                else:
                    self.last_distance = distance
            except:
                distance = self.last_distance

            # TODO: EXERCISE 4 - Angular Proportional Controller
            # Implement the angular controller to keep the object centered in the image.
            #
            # Suggested strategy:
            #   1. Compute the horizontal error between the image center ('center_x') 
            #      and the object's center ('cx').
            #   2. Apply a proportional controller: multiply the error by the gain 'self.k_yaw'.
            #   3. Clamp (limit) the resulting angular velocity so it does not exceed
            #      [-self.max_angular_speed, self.max_angular_speed].
            #      (Hint: you can use Python's built-in min() and max() functions)
            
            
            # --- Add your code here ---
            # error_yaw = ...
            # angular = ...
            twist.angular.z = float(angular)

            # TODO: EXERCISE 5 - Linear Proportional Controller
            # Implement the linear velocity controller so the robot
            # keeps a distance of 'self.desired_distance' from the object.
            #
            # Suggested strategy:
            #   1. Compute the distance error: 
            #      error = current distance - self.desired_distance
            #   2. Check if the absolute error is larger than 'self.dist_tolerance'.
            #      (Hint: use the built-in abs() function. If the error is smaller, 
            #      set linear speed to 0.0 to avoid jittering).
            #   3. If outside the tolerance, apply the proportional controller:
            #      multiply the error by the gain 'self.k_linear'.
            #   4. Clamp the resulting linear velocity so it does not exceed
            #      [-self.max_linear_speed, self.max_linear_speed].

            # --- Add your code here ---
            # error_dist = ...
            # ...

            twist.linear.x = float(linear)

            # visual debug
            cv2.putText(frame, f"Dist: {distance:.2f} m", (10,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.putText(frame, f"Conf: {best_conf:.2f}", (10,70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            target_found = True
            self.last_twist = twist
            self.last_detection_time = time.time()

        # -----------------------------
        # TARGET NOT FOUND
        # -----------------------------
        else:
            dt = time.time() - self.last_detection_time

            if dt < self.cmd_hold_time:
                twist = self.last_twist
            elif dt >= self.search_time_threshold:
                twist.linear.x = 0.0
                twist.angular.z = self.search_angular_speed
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0

        # PUBLISH COMMAND
        self.pub_vel.publish(twist)
        self.pub_debug.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))


def main(args=None):
    rclpy.init(args=args)
    node = OrangeFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.pub_vel.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()