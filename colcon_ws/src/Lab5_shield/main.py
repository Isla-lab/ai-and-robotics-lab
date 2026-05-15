import time
import random
import numpy as np
import torch
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from controller import get_nominal_action, get_safe_action

SAFETY_FILTER = False
def set_global_seed(seed: int = 42):
    """Fixed seed"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def main():
    set_global_seed(42)
    print("Connecting to coppelia...")
    client = RemoteAPIClient()
    sim = client.getObject('sim')
    
    script_owner = sim.getObject('/Floor') 
    script_handle = sim.getScript(sim.scripttype_childscript, script_owner)
    if script_handle == -1:
        script_handle = sim.getScript(sim.scripttype_customizationscript, script_owner)
    
    if script_handle == -1:
        print("ERROR: Script not found in /Floor.")
        return
        
    n_lidar = 20
    safe_action = [0.0, 0.0] # First step
    # 1. Get the handle for limo_1
    limo_handle = sim.getObject('/limo_1')
    
    # 2. Read the current position and orientation first
    # We do this to keep the exact Z height (floor level) and roll/pitch intact
    current_pos = sim.getObjectPosition(limo_handle, sim.handle_world)
    current_ori = sim.getObjectOrientation(limo_handle, sim.handle_world)
    
    # 3. Create the new arrays with your desired X, Y, and Yaw
    # current_pos[2] is the Z height. current_ori[0] and [1] are Roll and Pitch.
    new_pos = [-1.7, 0.74, current_pos[2]] 
    new_ori = [current_ori[0], current_ori[1], 0.0] # 0.0 radians = facing exactly "East" in Coppelia
    
    # 4. Teleport the robot
    sim.setObjectPosition(limo_handle, sim.handle_world, new_pos)
    sim.setObjectOrientation(limo_handle, sim.handle_world, new_ori)
    
    print(f"Robot reset to position: X={new_pos[0]}, Y={new_pos[1]}, Yaw=0.0")
    try:
        sim.startSimulation()
        print("Simulation started. Starting navigation...\n")
        
        while True:
            # =========================================================
            # STEP 1: Apply previous action and get the next
            # =========================================================
            raw_buffer = sim.callScriptFunction('step_centralizzato', script_handle, safe_action)
            
            data_array = np.frombuffer(raw_buffer, dtype=np.float32)
            lidar_data = data_array[:n_lidar]
    
            distance = data_array[n_lidar]
            angle = data_array[n_lidar + 1]
            min_lidar_dist = np.min(lidar_data)* 5.0
            
            if min_lidar_dist < 0.02:  
                print(f"\n💥 [CRASH] Obstacle hit! (distance Lidar: {min_lidar_dist:.3f}m)")
                
                # 1. Send [0.0, 0.0] velocity to CoppeliaSim to stop the wheels physically
                sim.callScriptFunction('step_centralizzato', script_handle, [0.0, 0.0])
                
                # 2. Break out of the while True loop to end the script
                break
            if distance < 0.1:
                print("\n[SUCCESS] Goal reached!")
                break
            
            # =========================================================
            # STEP 2: Get nominal policy
            # =========================================================
            v_nom, w_nom = get_nominal_action(distance, angle, lidar_data)
            
            # =========================================================
            # STEP 3: Safety filter (CBF)
            # =========================================================
            if SAFETY_FILTER:
                safe_action = get_safe_action(v_nom, w_nom, lidar_data)
            
                # =========================================================
                # DEBUG: Check filter 
                # =========================================================
                
                diff_v = abs(v_nom - safe_action[0])
                diff_w = abs(w_nom - safe_action[1])
                
                if diff_v > 0.01 or diff_w > 0.01:
                    status = "⚠️ CBF ACTIVE"
                else:
                    status = "✅ CLEAR"
                
                print(f"[{status}] Dist: {distance:.2f}m | Nominal: [{v_nom:.2f}, {w_nom:.2f}] -> Applied: [{safe_action[0]:.2f}, {safe_action[1]:.2f}]")
            else:
                safe_action = [v_nom, w_nom]
                status = "Clean policy"
                print(f"[{status}] Dist: {distance:.2f}m | Nominal: [{v_nom:.2f}, {w_nom:.2f}] -> Applied: [{safe_action[0]:.2f}, {safe_action[1]:.2f}]")

           
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n Interrupted from keyboard")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        sim.stopSimulation()
        print("Stopped simulation.")

if __name__ == '__main__':
    main()