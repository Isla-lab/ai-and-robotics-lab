
import random
import numpy as np
from mcts_planner.dynamic import OmnidirectionalRobot

SEED = 0
np.random.seed(SEED)
random.seed(SEED)

class Simulator():
    def __init__(self, params):
        self.params = params
        self.Q = np.diag([0.1, 1, 1, 1])
        self.R = np.diag([0.1, 0.1, 0.1, 0.1])
        self.dt = self.params['dt']
        self.n_actions = self.params['n_actions']
        self.omni_robot = OmnidirectionalRobot()
        # Position, velocities
        self.obstacles = [
            (np.array([1.60, -0.82]), np.array([0.0, 0.0])),
            (np.array([-12.4, 4.1])  , np.array([0.0, 0.0])),
            (np.array([15.0, -10.12]) , np.array([0.0, 0.0])),
            (np.array([-11.6, 10.1])  , np.array([0.0, 0.0])),
            (np.array([-11.7, 12.47]) , np.array([0.0, 0.0])),
            (np.array([11.60, -10.82]), np.array([0.0, 0.0])),
            (np.array([11.60, -10.82]), np.array([0.0, 0.0])),
            (np.array([-13.875, -21.52]), np.array([0.0, 0.0])),
            ]
                   


    def make_action(self, state):
        pass

    def take_action(self, x, x_d, u, obs_front, obs_back):
        x_dot = self.omni_robot.kinematic_model(x, u)
        x_new = self.euler_integrator(x, x_dot)
        r = self.reward(x_new, x_d, u, obs_front, obs_back)
        return x_new, r

    def try_action(self, x, u):
        x_dot = self.omni_robot.kinematic_model(x, u)
        x_new = self.euler_integrator(x, x_dot)
        return x_new

    def euler_integrator(self, x, x_dot):
        state = x + self.dt * x_dot
        return state

    def state_constraint(self, x):
        if x[1] >= 2 or x[2] >= 2 or x[3] >= 2:
            return False
        else:
            return True

    def compute_distance(self, obs_front, obs_back):
        min_dist_front = min(obs_front)
        min_dist_back = min(obs_back)
        min_dist = min(min_dist_front, min_dist_back)
        if min_dist < 1.0:
            return 1/min_dist
        else:
            return min_dist
        

    def reward(self, x_new, x_d, u, obs_front, obs_back):
        state_cost = x_new
        
        #TODO assign penalty based on velocity_obstacle_penalty (obstacle_radius = 0.5, robot_radius = 0.2)  
        # hint robot_pos argument should be the new_state
        penalty = ...
        
        #TODO ADD penalty to e
        e = abs(x_d[0] - state_cost[0]) + abs(x_d[1] - state_cost[1]) #  + ...
        return -e
    

    def velocity_obstacle_penalty(self, robot_pos, action, obstacle_radius, robot_radius, dt=0.1):
        x, y, theta = robot_pos
        v, omega = action

        # Predict velocity vector
        vx = v * np.cos(theta)
        vy = v * np.sin(theta)
        vel = np.array([vx, vy])
        v_norm = np.linalg.norm(vel)

        # Normalize angles between -pi and pi 
        def normalize_angle(a):
            return (a + np.pi) % (2 * np.pi) - np.pi

        # Initialize global_penalty
        max_penalty = 0.0

        for obs_pos, obs_vel in self.obstacles:
            x_obs, y_obs = obs_pos

            #TODO 
            # Compute the Relative position obstacle -> robot
            

            # Compute the Safety distance as sum of radius
           

            # compute the distance to obstacle
            

            # Check if distance is greather of 1 then "return" continue
            

            # Compute angle to obstacle with the arctan2
            

            # Compute half-angle of the cone using the safety radius and distance
           

            # Compute the cone bounds adding/subtracting the angle to the obstacle and the half-angle
            

            # Compute the  direction of motion with the arctan2 using vel 
            

            
            left_bound = normalize_angle(left_bound)
            right_bound = normalize_angle(right_bound)
            motion_angle = normalize_angle(motion_angle)

            # Check if motion angle falls inside the cone
            inside_cone = False
            if left_bound < right_bound:
                # Cone crosses the -pi/pi boundary
                if motion_angle > right_bound or motion_angle < left_bound:
                    inside_cone = True
            else:
                if right_bound < motion_angle < left_bound:
                    inside_cone = True

            # Return penalty
            if inside_cone:
               
                current_penalty = 1.0 #unsafe
                if current_penalty > max_penalty:
                    max_penalty = current_penalty

        return max_penalty
