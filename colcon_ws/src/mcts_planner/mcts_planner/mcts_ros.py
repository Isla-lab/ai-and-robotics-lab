import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import numpy as np
from mcts_planner.utils import quaternion_to_euler
from mcts_planner.mcts import MCTS
from rclpy.wait_for_message import wait_for_message

np.random.seed(0)


class MctsRos(Node):

    def __init__(self):
        super().__init__('minimal_publisher')


        self.angle_min, self.angle_max, self.angle_increment = 0, 0, 0
        self.th = 1.5
        self.index = 0.0
        self.ranges_front, self.ranges_back = [], []
        self.robot_state = []
        self.msg_twist = Twist()
        
        self.publisher_vel = self.create_publisher(Twist, '/cmd_vel', 1)
        self.subscription_front_scan = self.create_subscription(LaserScan, '/scan', self.front_laser_callback, rclpy.qos.qos_profile_sensor_data)
        self.subscription_odom = self.create_subscription(Odometry,'/odom', self.odom_callback, 1)

        odom_msg = wait_for_message(Odometry, self, '/odom')
        laser_msg = wait_for_message(LaserScan, self, '/scan')
        self.mcts = MCTS(debug=True)
        self.dt = self.mcts.params['dt']
        self.timer = self.create_timer(self.dt, self.control_loop)


    def front_laser_callback(self, msg):

        self.angle_min = msg.angle_min
        self.angle_max = msg.angle_max
        self.angle_increment = msg.angle_increment
        self.ranges_front = msg.ranges

    def back_laser_callback(self, msg):

        self.angle_min = msg.angle_min
        self.angle_max = msg.angle_max
        self.angle_increment = msg.angle_increment
        self.ranges_back = msg.ranges
        
    def odom_callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        theta = quaternion_to_euler(q)[2]
        self.robot_state = [x, y, theta]

    def control_loop(self):
        
        x, u = self.mcts.solver(self.robot_state, self.ranges_front, self.ranges_back)


        if np.sqrt((self.mcts.x_desired[0] - x[0])**2 + (self.mcts.x_desired[1] - x[1])**2) <= self.th: # and abs(x_new[2] - self.x_desired[2]) <= self.th:
            self.get_logger().info("Finish!!")
            self.msg_twist.linear.x = 0.0
            self.msg_twist.linear.y = 0.0
            self.msg_twist.angular.z = 0.0
            self.publisher_vel.publish(self.msg_twist)
            return
            
        else:
            self.msg_twist.linear.x = u[0]
            self.msg_twist.angular.z = u[1]
            self.publisher_vel.publish(self.msg_twist)

        self.index += 1
        self.get_logger().info(f"Timestap: {self.index/self.dt}")

        


def main(args=None):
    rclpy.init(args=args)

    mcts_ros = MctsRos()

    rclpy.spin(mcts_ros)

    mcts_ros.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()