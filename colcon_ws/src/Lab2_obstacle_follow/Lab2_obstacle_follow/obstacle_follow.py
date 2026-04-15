#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

import cv2
import numpy as np
import math
import time

from ultralytics import YOLO
# =============================================
# STUDENT EXERCISE: Vision-based target following
# with depth + LiDAR obstacle avoidance
#
# Objectives:
# 1) Track an orange ball using YOLO and depth camera
# 2) Maintain a desired distance from the target
# 3) Avoid obstacles using LiDAR readings
# 4) Fuse visual attraction with repulsive obstacle avoidance
# 5) Adjust speed during avoidance for safety
#
# Instructions:
# - Complete the TODOs in the code
# - Experiment with gains (k_cam, k_linear, k_obs)
# - Test in simulation (Coppelia/ROS 2) or real robot
# - Observe the effect of repulsion and sensor fusion
#
# =============================================

class SmartFollowerOrange(Node):

    def __init__(self):
        super().__init__('smart_follower_orange')

        # -------- VISION PARAMETERS --------
        self.target_class = "orange"
        self.conf_threshold = 0.15
        self.k_cam = 0.003

        # -------- DISTANCE CONTROL USING DEPTH --------
        self.desired_distance = 0.8
        self.dist_tolerance = 0.1
        self.k_linear = 0.5

        # -------- SPEED LIMITS --------
        self.max_linear_speed = 0.25
        self.max_angular_speed = 0.8
        self.search_speed = 0.3

        # -------- OBSTACLE AVOIDANCE --------
        self.safe_distance = 0.65
        self.k_obs = 0.8
        self.repulsive_turn = 0.0

        # -------- DEPTH --------
        self.depth_frame = None
        self.last_distance = self.desired_distance

        # -------- STATE --------
        self.target_visible = False
        self.target_center_x = 0
        self.last_twist = Twist()
        self.last_detection_time = 0.0

        # -------- ROS --------
        self.sub_img = self.create_subscription(
            Image,
            '/camera/color/image_raw',
            self.image_callback,
            10)

        self.sub_depth = self.create_subscription(
            Image,
            '/camera/depth/image_raw',
            self.depth_callback,
            10)

        self.sub_scan = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)

        self.pub_debug = self.create_publisher(
            Image,
            '/yolo/debug_image',
            10)

        # -------- YOLO --------
        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")

        self.get_logger().info("Smart Follower Orange with depth + LiDAR started.")

    # ------------------------------------------------
    # DEPTH CALLBACK
    # ------------------------------------------------
    def depth_callback(self, msg):

        try:
            self.depth_frame = self.bridge.imgmsg_to_cv2(msg, "32FC1")
        except:
            pass

    # ------------------------------------------------
    # LIDAR CALLBACK
    # ------------------------------------------------
    def scan_callback(self, msg: LaserScan):

        ranges = np.array(msg.ranges)

        # TODO (LiDAR preprocessing):
        # The raw LaserScan may contain:
        #   - NaN values
        #   - infinite values
        #   - zero readings
        #
        # Replace invalid measurements with a large distance (e.g. 10 meters)
        # so they do not affect obstacle detection.


        n = len(ranges)
        angles = msg.angle_min + np.arange(n) * msg.angle_increment

        # Ignore LiDAR rays where the ball is located
        if self.target_visible:

            fov_camera = 60 * np.pi / 180
            w = 640
            cx = self.target_center_x

            theta_box_center = (cx - w/2)/(w/2) * (fov_camera/2)

            box_half_angle = 0.05

            mask = (angles > (theta_box_center - box_half_angle)) & \
                   (angles < (theta_box_center + box_half_angle))

            ranges[mask] = 10.0

        # TODO:
        # 1) Split the LiDAR measurements into left and right sectors
        # 2) Compute the minimum distance in each sector
        # Hint: angles > 0 -> left, angles < 0 -> right

        # TODO (Repulsive behaviour):
        # Implement a turning behaviour based on obstacle proximity
        # The closer the obstacle, the stronger the turn
        # Clip the final angular speed to [-max_angular_speed, max_angular_speed]

    # ------------------------------------------------
    # IMAGE CALLBACK
    # ------------------------------------------------
    def image_callback(self, msg):

        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except:
            return

        h, w, _ = frame.shape
        center_screen = w // 2

        self.target_center_x = 0

        results = self.model.predict(
            frame,
            verbose=False,
            conf=self.conf_threshold)

        best_target = None
        max_area = 0
        best_conf = 0.0

        # -------- FIND TARGET --------
        for r in results:
            for box in r.boxes:

                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                conf = float(box.conf[0])

                if cls_name == self.target_class:

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    area = (x2 - x1) * (y2 - y1)

                    if area > max_area:
                        max_area = area
                        best_target = (x1, y1, x2, y2)
                        best_conf = conf

        twist = Twist()

        # ------------------------------------------------
        # TARGET FOUND
        # ------------------------------------------------
        if best_target:

            self.target_visible = True

            x1, y1, x2, y2 = best_target

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            self.target_center_x = cx

            # -------- DEPTH DISTANCE --------

            distance = self.last_distance

            if self.depth_frame is not None:

                try:

                    window = self.depth_frame[
                        max(cy-2,0):cy+3,
                        max(cx-2,0):cx+3]

                    dist = float(np.nanmean(window))

                    if not math.isnan(dist) and dist > 0:
                        distance = dist

                        # simple low-pass filter
                        distance = 0.7*self.last_distance + 0.3*distance

                        self.last_distance = distance

                except:
                    pass

            # -------- ANGULAR CONTROL --------

            error_yaw = center_screen - cx

            # TODO (Sensor fusion):
            # Combine the visual attraction (towards the target)
            # with the repulsion from obstacles (repulsive_turn)
            # to compute the final angular velocity.
            

            angular = np.clip(
                angular,
                -self.max_angular_speed,
                self.max_angular_speed)

            twist.angular.z = float(angular)

            # -------- LINEAR CONTROL --------

            error_dist = distance - self.desired_distance

            if abs(error_dist) > self.dist_tolerance:

                linear = self.k_linear * error_dist

                if abs(self.repulsive_turn) > 0.2:
                    linear *= 0.3

            else:
                linear = 0.0

            linear = np.clip(
                linear,
                0.0,
                self.max_linear_speed)

            twist.linear.x = float(linear)

            # -------- DEBUG --------

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,165,255),2)

            cv2.circle(frame,(cx,cy),5,(0,255,0),-1)

            cv2.putText(frame,
                        f"Dist: {distance:.2f} m",
                        (10,40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (255,255,0),
                        2)

            cv2.putText(frame,
                        f"Conf: {best_conf:.2f}",
                        (10,70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0,255,255),
                        2)

            if abs(self.repulsive_turn) > 0.1:

                cv2.putText(frame,
                            "AVOIDING",
                            (10,100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0,0,255),
                            2)

            else:

                cv2.putText(frame,
                            "TRACKING",
                            (10,100),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0,255,0),
                            2)

            self.last_twist = twist
            self.last_detection_time = time.time()

        # ------------------------------------------------
        # TARGET NOT FOUND
        # ------------------------------------------------
        else:

            self.target_visible = False

            dt = time.time() - self.last_detection_time

            if dt < 0.3:

                twist = self.last_twist

            else:

                twist.linear.x = 0.0
                twist.angular.z = self.search_speed

            cv2.putText(frame,
                        "SEARCHING...",
                        (50,h//2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255,165,0),
                        2)

        self.pub_vel.publish(twist)

        self.pub_debug.publish(
            self.bridge.cv2_to_imgmsg(frame,"bgr8"))


def main(args=None):

    rclpy.init(args=args)

    node = SmartFollowerOrange()

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