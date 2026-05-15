import numpy as np
import cvxpy as cp
from stable_baselines3 import PPO

CHECKPOINT_PATH = # TODO: model path
model = PPO.load(CHECKPOINT_PATH)
print(f"Loaded RL Policy from {CHECKPOINT_PATH}")

# Parameters
L_LOOKAHEAD = 0.35      
R_SAFE = 0.30           
GAMMA = 2.0  
LIDAR_MAX_DIST = 5.0    
LIDAR_FOV = np.pi * 0.8 

DIST_NORM_MAX = 7.0

def get_nominal_action(distance, angle, lidar_data):
    """
    1. RL POLICY: Calculates the nominal action through the trained PPO policy
    """
    lidar_norm = np.clip(lidar_data / LIDAR_MAX_DIST, 0.0, 1.0)
    dist_norm  = np.clip(distance / DIST_NORM_MAX, 0.0, 1.0)
    obs = np.concatenate(
        [lidar_norm, [dist_norm, np.cos(angle), np.sin(angle)]]
    ).astype(np.float32)
    action, _ = model.predict(obs, deterministic=True)
    v_nom = float(np.clip(action[0], 0.0, 1.0))
    w_nom = float(np.clip(action[1], -1.0, 1.0))
    return v_nom, w_nom

def get_safe_action(v_nom, w_nom, lidar_data):
    """
    2. SAFETY FILTER: Takes the nominal action and filters it through CBF 
    """
    actual_distances = lidar_data * LIDAR_MAX_DIST
    angles = np.linspace(-LIDAR_FOV/2, LIDAR_FOV/2, len(lidar_data))
    
    A_list = []
    b_list = []
    
    # Constraint construction for each lidar
    for d, alpha in zip(actual_distances, angles):
        if d >= LIDAR_MAX_DIST - 0.05:
            continue
            
        x_obs = d * np.cos(alpha)
        y_obs = d * np.sin(alpha)

        
        # TODO: implement the CBF 
        # hint: use the lookahead point for the x coordinate
        h = 
        
        # TODO: derivate to get the two input closed form
        A_v = #
        A_w = #
        #TODO: Right Hand Side of CBF definition        
        b_val = #
        
        A_list.append([A_v, A_w])
        b_list.append(b_val)
        
    # If there are no problems we can avoid the QP computation
    if len(A_list) == 0:
        return [v_nom, w_nom]
        
    A = np.array(A_list)
    b = np.array(b_list)
    
    # Definition and solution of the QP
    u = cp.Variable(2)
    u_nom_arr = np.array([v_nom, w_nom])
    Q = np.diag([1.0, 0.5]) 
    
    cost = cp.quad_form(u - u_nom_arr, Q)
    objective = cp.Minimize(cost)
    
    constraints = [
        A @ u <= b, 
        u[0] >= 0.1,         
        u[0] <= 0.7,         
        u[1] >= -1.0,        
        u[1] <= 1.0          
    ]
    
    prob = cp.Problem(objective, constraints)
    
    try:
        prob.solve(solver=cp.OSQP, verbose=False)
        if prob.status == cp.OPTIMAL:
            return [float(u.value[0]), float(u.value[1])]
        else:
            return [0.0, 0.0] # emergency fallback 
    except Exception:
        return [0.0, 0.0]