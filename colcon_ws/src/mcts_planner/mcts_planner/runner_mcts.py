#!/usr/bin/env python3

import time
from mcts import MCTS
import sys
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from datetime import datetime


class Runner:

    def __init__(self):

        # Call mcts_linear
        self.mcts = MCTS(debug=True)
        self.T = 10  # Total simulation time
        self.timesteps = int(self.T / self.mcts.params['dt'])
        before = time.time()
        self.optimal_actions, self.optimal_states, cost_history = self.mcts.solver(self.timesteps)
        after = time.time()
        print('Time elapsed:', "{:.4f}".format(after-before), 'second(s)')

        #self.save_pdf(self.optimal_states, self.optimal_actions, cost_history)
        self.make_plots(self.optimal_actions, self.optimal_states)
        #self.make_plots()
        # self.visualizer.animate_agents(self.path, True)


    def save_pdf(self, x_hist, u_hist, cost_history):
        # Assume x_hist and u_hist are already defined

        # Convert numpy arrays to DataFrames
        x_hist_df = pd.DataFrame(x_hist, columns=[f"x_{i}" for i in range(x_hist.shape[1])])
        u_hist_df = pd.DataFrame(u_hist, columns=[f"u_{i}" for i in range(u_hist.shape[1])])
        cost_hist_df = pd.DataFrame(cost_history, columns=[f"c_{i}" for i in range(cost_history.shape[1])])

        # Concatenate dataframes along columns
        data = pd.concat([x_hist_df, u_hist_df, cost_hist_df], axis=1)

        # Concatenate dataframes along columns
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
        # Save to CSV
        data.to_csv("results/" + dt_string + "_mcts.csv", index=False)


    def make_plots(self, optimal_actions, x_hist):
        x_min, x_max = -2.5, 2.5  # X boundaries
        y_min, y_max = -2.5, 2.5  # Y boundaries
        time = np.linspace(0, self.T, self.timesteps)
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))


        ax[0].scatter(x_hist[:, 0], x_hist[:, 1])
        ax[0].quiver(self.mcts.x0[0], self.mcts.x0[1], np.cos(self.mcts.x0[2]), np.sin(self.mcts.x0[2]),
                   angles='xy', scale_units='xy', scale=1, color='blue', width=0.005)

        # Plot p, q, r states
        # plt.subplot(2, 1, 1)
        # plt.plot(time, x_hist[:, 1], label='p (roll rate)')
        # plt.plot(time, x_hist[:, 2], label='q (pitch rate)')
        # plt.plot(time, x_hist[:, 3], label='r (yaw rate)')
        # plt.title('State Evolution')
        # plt.xlabel('Time [s]')
        # plt.ylabel('Rates [rad/s]')
        # plt.legend()
        #
        # # Plot control inputs
        # plt.subplot(2, 1, 2)
        # plt.plot(time, u_hist[:, 1], label='delta_e (elevator)')
        # plt.plot(time, u_hist[:, 2], label='delta_a (aileron)')
        # plt.plot(time, u_hist[:, 3], label='delta_r (rudder)')
        # plt.title('Control Inputs')
        # plt.xlabel('Time [s]')
        # plt.ylabel('Control Surface Deflections [rad]')
        # plt.legend()
        #
        # plt.tight_layout()
        ax[0].set_xlim([x_min, x_max])
        ax[0].set_ylim([y_min, y_max])

        plt.show()

if __name__ == '__main__':
    r = Runner()
