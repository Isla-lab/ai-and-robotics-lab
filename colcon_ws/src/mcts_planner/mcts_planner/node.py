import random
import math

import numpy as np

np.random.seed(0)

class Node:
    def __init__(self, state):
        self.state = state
        self.parent = None
        self.children = []
        self.visits = 0
        self.score = 0.0
        self.action = []
        self.id = 0


    def select_child(self, c):
        best_child = None
        best_ucb = -float('inf')
        for child in self.children:
            if child.visits == 0:
                ucb = float('inf')  # Assign a large value for unvisited nodes
            else:
                ucb = child.score / child.visits + c * math.sqrt(2 * math.log(self.visits) / child.visits)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
        return best_child

    def expand(self, simulator, node, action_space):
        states, actions = self.possibile_state(simulator, node, action_space)
        for i in range(0, len(states)):
            child_state = states[i]
            child = Node(child_state)
            child.parent = node
            node.action.append(actions[i])
            child.id = node.id + 1
            self.children.append(child) 


    def possibile_state(self, simulator, node, action_space):
        possible_states, possible_actions = [], []
        for i in range(simulator.n_actions):
            # u sample from distribution
            u = action_space.multivariate_normal()
            #u = action_space.pdf_multivariate_normal(node.action)
            x = simulator.try_action(node.state, u)
            # while self.check_constraint(x):
            #     u = action_space.multivariate_normal()
            #     x = simulator.try_action(node.state, u)
            #     print("----------")
            #     print(str(x[9]) + str(x[10]) + str(x[11]))
            possible_states.append(x)
            possible_actions.append(u)
        return possible_states, possible_actions

    def check_constraint(self, x):
        if x[9] >= 2 or x[10] >= 2 or x[11] >= 2:
            return True
        else:
            return False

    def backpropagate(self, score):
        self.visits += 1
        self.score += score
        if self.parent:
            self.parent.backpropagate(score)