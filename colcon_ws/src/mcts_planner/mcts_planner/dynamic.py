import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt
from tqdm import tqdm  # Import tqdm for progress bar

np.random.seed(0)

class OmnidirectionalRobot():
    def __init__(self):
        # Robot parameters
        self.r = 0.05  # Wheel radius (m)
        self.l = 0.2  # Distance from center to wheel along x (m)
        self.w = 0.2  # Distance from center to wheel along y (m)
        self.m = 5.0  # Mass of robot (kg)
        self.I_z = 0.5  # Moment of inertia (kg.m^2)
        self.dt = 0.01

        # Transformation matrix from wheel speeds to velocity
        self.T_wheels = (self.r / 4) * np.array([
            [1, 1, 1, 1],
            [-1, 1, 1, -1],
            [-1 / (self.l + self.w), 1 / (self.l + self.w), -1 / (self.l + self.w), 1 / (self.l + self.w)]
        ])


    def euler_integrator(self, x_dot, x):
        x_new = np.zeros(len(x_dot))
        for i in range(len(x_dot)):
            x_new[i] = x[i] + x_dot[i] * self.dt
        return x_new

    def kinematic_model(self, state, body_velocities):
        """
        Computes the kinematic transformation from body velocities to world velocities.

        state: [x, y, theta]
        body_velocities: [v_x, v_y, omega] in the body frame

        Returns [x_dot, y_dot, theta_dot] in the world frame.
        """
        x, y, theta = state
        v_x, omega = body_velocities

        # Convert body velocities to world-frame velocities
        x_dot = v_x * np.cos(theta) 
        y_dot = v_x * np.sin(theta) 
        theta_dot = omega

        return np.array([x_dot, y_dot, theta_dot])


    def dynamic_model(self, omega_wheels):
        """
        Computes the body velocities from wheel speeds.

        omega_wheels: [omega_1, omega_2, omega_3, omega_4] (rad/s)

        Returns [v_x, v_y, omega] in the body frame.
        """
        F_x, F_y, M_z = self.T_wheels @ omega_wheels
        v_x_dot = F_x / self.m
        v_y_dot = F_y / self.m
        omega_dot = M_z / self.I_z
        return v_x_dot, v_y_dot, omega_dot


    def omnidirectional_dynamics(self, state, omega_wheels):
        """
        Full dynamics function for integration.

        state = [x, y, theta, v_x, v_y, omega]
        omega_wheels = [omega_1, omega_2, omega_3, omega_4]
        """
        x, y, theta, v_x, v_y, omega = state

        # Compute body velocities from wheel speeds
        body_velocities = self.dynamic_model(omega_wheels)  # [v_x, v_y, omega]

        vel = self.euler_integrator(body_velocities, [v_x, v_y, omega])

        # Compute world-frame velocities
        world_velocities = self.kinematic_model([x, y, theta], vel)

        pos = self.euler_integrator(world_velocities, [x, y, theta])

        return np.concatenate((pos, vel))



def main():

    # Initial state [x, y, theta, v_x, v_y, omega]
    state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    T = 20
    robot = OmnidirectionalRobot()
    timesteps = int(T / robot.dt)
    x_hist = np.zeros((timesteps, len(state)))
    for i in tqdm(range(timesteps), desc="Simulation Progress"):

        # Constant wheel speeds (rad/s)
        omega_wheels = np.array([-10.0, 10.0, 10.0, -10.0])

        state = robot.omnidirectional_dynamics(state, omega_wheels)
        x_hist[i, :] = state


    time = np.linspace(0, T, timesteps)
    # Plot results
    plt.figure(figsize=(10, 5))

    # Position plot
    plt.subplot(1, 2, 1)
    plt.plot(x_hist[:, 0], x_hist[:, 1], label="Robot Path")
    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.title("Robot Trajectory")
    plt.legend()
    plt.grid()


    plt.show()

if __name__ == '__main__':
    main()