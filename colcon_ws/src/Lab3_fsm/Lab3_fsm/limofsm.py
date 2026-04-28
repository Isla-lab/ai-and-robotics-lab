#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import math
import numpy as np
#TODO add depth camera so know when to stop at a sign? now if recognized just executes and avoids reusing the same signal twice in row
#TODO check lidar / do angle increment

class LimoFSM(Node):
    def __init__(self):
        super().__init__('fsm_node')

        # --- ROS PUBLISHERS & SUBSCRIBERS ---
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)               # Command velocity
        self.create_subscription(String, '/traffic_sign', self.sign_callback, 10) # Traffic signs detected
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)       # Robot position & orientation
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)     # LiDAR readings

        # --- FSM STATE VARIABLES ---
        # states sequence: START -> RED_LIGHT -> CRUISE_70 -> STOP_WAIT -> CRUISE_AFTER_STOP -> SLOW_30 -> WALL_FOLLOW_RIGHT -> ALIGN_90_RIGHT -> GOAL
        self.state = "START"
        self.current_yaw = 0.0          # Current heading (yaw)
        self.current_pos = (0.0, 0.0)   # Current x,y position
        self.last_sign = ""             # Last detected traffic sign

        # LiDAR & timing
        self.wall_detected_right = False
        self.stop_start_time = None
        self.wall_lost_time = None
        self.lidar_threshold = 1.0
        # Timer for periodic control loop
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Optimized FSM started. Current state: START")

    # --- CALLBACK: Traffic Sign Detection ---
    def sign_callback(self, msg):
        sign = msg.data
        if sign == self.last_sign:
            return  # Ignore repeated detections
        self.last_sign = sign
        self.get_logger().info(f"YOLO detected: {sign}")

        # State transitions based on detected signs
        if sign == "Red Light" and self.state == "START":
            #TODO
        elif sign == "Green Light" and self.state == "RED_LIGHT":
            #TODO
        elif sign == "Stop" and self.state in ["CRUISE_70", "SLOW_30"]:
            self.stop_start_time = self.get_clock().now()
            #TODO
        elif sign == "Speed Limit 30" and self.state == "CRUISE_AFTER_STOP":
            #TODO

    # --- CALLBACK: Odometry updates ---
    def odom_callback(self, msg):
        # Update current position
        self.current_pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
        # Convert quaternion to yaw
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    # --- CALLBACK: LiDAR readings ---
    def lidar_callback(self, msg):
        n = len(msg.ranges)
        angles = msg.angle_min + np.arange(n) * msg.angle_increment

        right_ranges = np.array(msg.ranges)[60:120]  
        left_ranges  = np.array(msg.ranges)[0:60]   

        
        right_ranges = np.nan_to_num(right_ranges, nan=self.lidar_threshold, posinf=self.lidar_threshold, neginf=self.lidar_threshold)
        left_ranges = np.nan_to_num(left_ranges, nan=self.lidar_threshold, posinf=self.lidar_threshold, neginf=self.lidar_threshold)

        self.wall_detected_right = #TODO
        self.wall_detected_left = #TODO

    # --- FSM STATE TRANSITION ---
    def change_state(self, new_state):
        if self.state != new_state:
            self.get_logger().info(f"TRANSITION: {self.state} -> {new_state}")
            self.state = new_state
            self.wall_lost_time = None  # Reset timer when entering new state

    # --- CONTROL LOOP (runs periodically) ---
    def control_loop(self):
        twist = Twist()  # Initialize command

        #TODO implement START state behavior
        if self.state == 

        #TODO implement RED_LIGHT state behavior
        elif self.state == 

        #TODO implement CRUISE_70 state behavior (0.7 m/s)
        elif self.state == 

        #TODO implement STOP_WAIT state behavior
        elif self.state == 
            twist.linear.x = #TODO
            # Non-blocking wait for 2 seconds
            elapsed = (self.get_clock().now() - self.stop_start_time).nanoseconds / 1e9
            if elapsed >= 2.0:
                
        #TODO implement CRUISE_AFTER_STOP behavior (0.4m/s)
        elif self.state == 

        #TODO implement SLOW_30 state behavior (0.3 m/s), if a wall is detected on the right it should move to state WALL_FOLLOW_RIGHT
        elif self.state == 

        elif self.state == "WALL_FOLLOW_RIGHT":
            twist.linear.x = 0.5  # Forward while following wall
            if not self.wall_detected_right:
                if self.wall_lost_time is None:
                    self.wall_lost_time = self.get_clock().now()
                
                #TODO Wait 2.7 sec before turning if wall lost and move to ALIGN_90_RIGHT

        #TODO implement ALIGN_90_RIGHT behavior
        # Align to -1.57 degree and move to FINAL_STRAIGHT state
        elif self.state == 

        #TODO implement FINAL_STRAIGHT
        #Move forward, if x < -0.5 then change state to GOAL
        elif self.state == 

        elif self.state == "GOAL":
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().info("GOAL REACHED")

        # Publish velocity command
        self.cmd_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LimoFSM()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()