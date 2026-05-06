from mcts_planner.node import Node
import os
import yaml
import numpy as np
from mcts_planner.action_space import ActionSpace
from mcts_planner.simulator import Simulator
from tqdm import tqdm  # Import tqdm for progress bar

np.random.seed(0)
class MCTS():

    def __init__(self, debug):
        self.debug = debug
        self.params = self.load_params()
        self.simulator = Simulator(self.params)
        self.x_desired = self.params['x_desired']
        self.m=2
        self.th = 0.1
        self.mu = np.array([0.0, 0.0])
        self.sigma = np.diag([0.5, 0.5])
        self.obs_front, self.obs_back = [], []
        self.action_space = ActionSpace(self.m, mu=self.mu, sigma=self.sigma)


    
    def solver(self, x0, obs_front, obs_back):
        root = Node(x0)
        self.obs_front = obs_front
        self.obs_back = obs_back
        best_child_uct, promising_action = self.mcts(root)
        x = best_child_uct.state
        u = promising_action
        
        
        print("Best state is: " + str(x))
        print("Best action is: " + str(u))

        return x, u

    def mcts(self, root):
        j = 0
        max_depht = self.params['max_depht']
        discount = self.params['discount']
        H = self.params['H']
        depth_tree = 0
        # simulation
        while j < self.params['n_simulation']: #CHANGED was <=
            node = root
            # selection
            while node.children:
                node = node.select_child(self.params['c'])
            # expansion
            if node.visits == 0 and depth_tree < H:
                node.expand(self.simulator, node, self.action_space)
                depth_tree = depth_tree + 1
            # rollout
            depth = 0
            #u = self.action_space.multivariate_normal()
            #R = self.rollout(node, depth, max_depht, discount, u)
            R = self.rollout_dyn( node, -1, 1, max_depth=max_depht)
            # backpropagation
            node.backpropagate(R)
            j = j + 1
        best_child = max(root.children, key=lambda child: child.visits)
        best_child_uct = root.select_child(0)
        #best_child = self.get_best_child(root)
        id = root.children.index(best_child_uct)
        promising_action = root.action[id]
        return best_child_uct, promising_action

    def get_best_child(self, root):
        v_s = dict()
        max_v = None
        for action in root.children:
            max_v = action.visits if max_v is None else max(max_v, action.visits)
            v_s[action.visits] = action.action
        return v_s[max_v]

    def rollout_dyn(self, node, x_min, x_max, max_depth=10):
        current_state = node.state
        total_cost = 0
        u = self.action_space.multivariate_normal()
        for _ in range(max_depth):
            new_state, r = self.simulator.take_action(current_state, self.x_desired, u, self.obs_front, self.obs_back)

            

            total_cost += r
            current_state = new_state
        return total_cost

    def is_state_valid(self, state, x_min, x_max):
        """
        Check if the state satisfies the constraints.
        """
        partial_state = np.array([state[1], state[2], state[3]])
        return np.all(partial_state >= x_min) and np.all(partial_state <= x_max)

    def rollout(self, node, depth, max_depht, discount, u):
        if depth >= max_depht:
            return 0
        # random sampling on action
        #u = self.action_space.pdf_multivariate_normal(node.action)
        new_state, r = self.simulator.take_action(node.state, self.x_desired, u)
        child_state = new_state
        child = Node(child_state)
        child.action = u
        child.parent = node
        return r + discount * self.rollout(child, depth + 1, max_depht, discount, u)

    def load_params(self):    
        
        filename = "/home/ubuntu/Desktop/scoperta-main/src/mcts_planner/config/mcts_config.yaml" #TODO check this

        with open(filename, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return data






if __name__ == '__main__':
    MCTS()

