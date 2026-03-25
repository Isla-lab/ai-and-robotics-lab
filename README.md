# AI & Robotics Laboratory 2025/2026

Welcome to the AI & Robotics Laboratory! This repository contains the solutions, assignments, scenes, and code for the practical sessions of the course.

To ensure a smooth experience during the labs, you must configure your Ubuntu 22.04 environment with ROS2 Humble, Python 3, and the CoppeliaSim robotic simulator. We have provided an automated script to handle the heavy lifting and set up your local workspace.

Please follow this guide step-by-step.

---

## 1. Prerequisites: Download CoppeliaSim
Before running the setup script, you need to manually download the simulator.

1. Go to the official Coppelia Robotics website: [https://www.coppeliarobotics.com/](https://www.coppeliarobotics.com/)
2. Navigate to the **Downloads** section.
3. Download the **CoppeliaSim Edu** version for **Ubuntu 22.04** (`.tar.xz` file). 
4. **Important:** Leave the downloaded file exactly as it is in your default `Downloads` folder. The installation script will automatically find it.

## 2. Run the Installation Script
The `install_lab.sh` script will install ROS2 Humble, set up your system dependencies, configure Python (including YOLO), and **automatically create your workspace on your Desktop** (`~/Desktop/ai-and-robotics-lab`).

Open a terminal, navigate to the directory where you downloaded this repository, and run:

```bash
# Make the script executable
chmod +x install_lab.sh

# Run the installation script
./install_lab.sh
```

*Note: You may be prompted to enter your `sudo` password. The script will download several gigabytes of data, so please be patient.*

## 3. Running Lab 1
Once the installation is complete, **close your terminal and open a new one** to load all the new environment variables.

**Step 1: Launch the Simulator**
1. Navigate to your new workspace on the Desktop:
   ```bash
   cd ~/Desktop/ai-and-robotics-lab
   ```
2. Launch the simulator directly into the Lab 1 scene using the custom alias:
   ```bash
   coppelia scenes/follow_limo.ttt
   ```
3. Once the CoppeliaSim window opens, click the **Play** button (▶) in the top toolbar to start the simulation.

4. **Verify the connection:** Open a **new terminal** and list the active ROS2 topics to ensure the simulator is broadcasting data correctly:
   ```bash
   ros2 topic list
   ```
   You should see an output similar to this:
   ```text
   /camera/color/image_raw
   /camera/depth/image_raw
   /cmd_vel
   /image
   /odom
   /parameter_events
   /rosout
   /scan
   /simTime12710
   /tf
   ```
   *(Note: the number after `simTime` will vary).*

## 4. How to add future Labs (e.g., Lab 2)
As the course progresses, new labs will be released. You **do not** need to run the setup script again. Just follow these steps:

1. **Download the new package** from this GitHub repository (e.g., the `Lab_2` folder).
2. **Move it** into your local source folder on the Desktop:
   `~/Desktop/ai-and-robotics-lab/colcon_ws/src/`
3. **Register the new package** in ROS2 by opening a terminal and compiling the workspace:
   ```bash
   cd ~/Desktop/ai-and-robotics-lab/colcon_ws
   colcon build --symlink-install
   ```
4. **Restart the terminal.** Close the current terminal and open a new one. You can now use `ros2 run` with the new package!

---
