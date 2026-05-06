import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import multivariate_normal
from scipy.integrate import quad

np.random.seed(0)

class ActionSpace():
    def __init__(self, m, mu, sigma):
        # Initialize the parameters
        self.m = m  # Dimension of control variables
        self.mu = mu  # Initial mean vector (can be set to any reasonable value)
        self.sigma = sigma  # Initial covariance matrix (identity matrix as an example)
        self.u_min = np.array([-1.0, -1.0, -1.0])  # Lower bound for the control variables
        self.u_max = np.array([1.0, 1.0, 1.0])  # Upper bound for the control variables
        self.eta = 0.5  # Learning rate


    # Multivariate normal PDF
    def pdf_multivariate_normal(self, u):
        """PDF of a multivariate normal distribution."""
        norm_const = 1.0 / np.sqrt((2 * np.pi) ** self.m * np.linalg.det(self.sigma))
        exp_term = np.exp(-0.5 * (u - self.mu).T @ np.linalg.inv(self.sigma) @ (u - self.mu))
        return norm_const * exp_term

    
    def multivariate_normal(self):
        u = np.random.multivariate_normal(self.mu, self.sigma)
        return u



    # Truncated PDF
    def truncated_pdf(self, u, mu, sigma, u_min, u_max):
        """Truncated PDF of a multivariate normal distribution."""
        # Compute the normal PDF
        f_u = self.pdf_multivariate_normal(u, mu, sigma)

        # Compute the integral for normalization over the truncated region
        integral = quad(lambda x: self.pdf_multivariate_normal(np.array([x]), mu, sigma), u_min[0], u_max[0])[0]

        # Calculate the truncated PDF
        return f_u / integral


    # Gradient-based update rule for mean and covariance
    def update_mean_covariance(self, mu, sigma, u_star, eta):
        """Update the mean and covariance matrix based on the optimal action u_star."""
        mu_new = mu + eta * (u_star - mu)
        outer_product = np.outer(u_star - mu, u_star - mu)
        sigma_new = sigma + eta * (outer_product - sigma)
        self.mu = mu_new
        self.sigma = sigma_new



def main():

    action_space = ActionSpace(3, np.zeros(3), np.eye(3))
    # Example: sample a control variable, compute its PDF, and update
    u_star = np.array([0.5, -0.3, 0.5])  # Example of optimal action (u*)
    u = [0, 0, 0]
    print(action_space.multivariate_normal(action_space.mu, action_space.sigma))
    pdf_value = action_space.pdf_multivariate_normal(u, action_space.mu, action_space.sigma)
    truncated_pdf_value = action_space.truncated_pdf(u_star, action_space.mu, action_space.sigma, action_space.u_min, action_space.u_max)

    # Update the mean and covariance matrix based on the optimal action u_star
    mu_new, sigma_new = action_space.update_mean_covariance(action_space.mu, action_space.sigma, u_star, action_space.eta)

    # Print results
    print("Initial mean:", action_space.mu)
    print("Updated mean:", mu_new)
    print("Initial covariance matrix:\n", action_space.sigma)
    print("Updated covariance matrix:\n", sigma_new)
    print("PDF value of u:", pdf_value)
    print("Truncated PDF value of u_star:", truncated_pdf_value)


if __name__ == '__main__':
    # Usage example
    main()
