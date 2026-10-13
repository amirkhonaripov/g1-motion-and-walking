# Text-prompted Unitree G1 motion, played in MuJoCo and rendered to MP4

A 5-second G1 motion was generated from a text prompt, exported as a LAFAN CSV, played back on the G1 model in MuJoCo, and rendered to `motion.mp4`

Tested with Python 3.12

## Inputs

- Prompt (also in `prompt.txt`): "A humanoid robot walks forward and kicks a ball with its right foot"
- Generator: UltimateBots Studio, Uthana TTM 3.0, target robot Unitree G1, export format CSV
- Clip length: 5 seconds. The file has 150 rows, so the frame rate is 30 fps. The CSV has no timestamps; I inferred the rate from the 5 s length shown by the tool

## Installation

Clone both repositories into the same parent folder, so they sit side by side:

```bash
git clone https://github.com/amirkhonaripov/g1-motion-and-walking.git
git clone https://github.com/unitreerobotics/unitree_rl_gym.git
cd g1-motion-and-walking/part_a
pip install -r requirements.txt
```

Resulting layout:

```
parent-folder/
├── g1-motion-and-walking/
└── unitree_rl_gym/
```

The model used is `unitree_rl_gym/resources/robots/g1_description/g1_29dof.xml`. I load this file directly and not `scene.xml`, because `scene.xml` includes the 12-DoF robot, and `g1_29dof.xml` already defines its own floor

`motion.csv` is included, so you can skip regenerating the motion. To regenerate it, use https://studio.ultimatebots.com/home with the prompt above

## How to run

From `part_a/`:

```bash
python play_motion.py motion.csv ../../unitree_rl_gym/resources/robots/g1_description/g1_29dof.xml
```

The CSV path comes first, then the XML path. The video is written as `motion.mp4` in the folder you run the command from (`part_a/` if you followed the steps above)

## How I worked out what the CSV columns are

The CSV has no header and no timestamp column. Each row is one frame, and each frame is a full pose of the robot. The layout I arrived at:

| Columns | Meaning | Main evidence |
|---|---|---|
| 0 to 2 | pelvis position x, y, z (meters) | step 6 |
| 3 to 6 | pelvis orientation, quaternion stored as x, y, z, w | steps 6 and 7 |
| 7 to 35 | 29 joint angles (radians), in the model's joint order | steps 3, 5 and 8 |

The files behind these steps are in `analysis/`. The steps, in the order I did them:

1. **Shape:** The file has 150 rows and 36 columns, and contains no header
2. **Matching a model:** A floating-base robot's pose is a base (position, 3 values, plus a quaternion orientation, 4 values) followed by one angle per joint. 36 - 7 = 29 joint angles, which points to the 29-DoF G1
3. **Checking the model:** I ran `analysis/inspect_model.py` on `g1_29dof.xml`. It reports `nq = 36`, the floating base joint at slot 0, and 29 hinge joints in slots 7 to 35, in a fixed order (`analysis/model_joints.txt`). This matches the 36 columns
4. **Listing the joints:** `model_joints.txt` was produced with `mujoco.mj_id2name` and `model.jnt_qposadr`. It gives each joint's name and the slot where it starts
5. **Which columns move:** `analysis/inspect_csv.py` computes the standard deviation of every column over the 150 frames. The ten largest were: pelvis y (column 1, 1.28 m), right_hip_pitch_joint (13, 0.46), left_hip_pitch_joint (7, 0.38), left_shoulder_pitch_joint (22, 0.35), right_shoulder_pitch_joint (29, 0.34), left_knee_joint (10, 0.29), left_shoulder_yaw_joint (24, 0.28), right_knee_joint (16, 0.28), left_ankle_pitch_joint (11, 0.20) and right_ankle_pitch_joint (17, 0.19). The ranking was used to sanity-check by matching the top columns to joint names using model_joints.txt. The pelvis, hips, knees and shoulders move the most, which is consistent with a walk plus a kick 
6. **Rotation values:** Looked at row 0's rotation values ([3:7] quaternions: 0.065, 0.061, -0.699, 0.709) and compared against the MjData's default pose ([3:7]: [1, 0, 0, 0]). Two values are large and two are near zero, which describes a turn around the vertical axis (a standing robot) only if the order is [x, y, z, w], while the default pose shows that MuJoCo expects [w, x, y, z]. Row 0's pelvis height (0.797) is close to the model's default (0.793), so the position is in meters
7. **Test of the quaternion order:** `analysis/frame0_test.py` renders frame 0 twice. Version A (`analysis/ver_a.png`) copies the rotation values as they are in the CSV, and version B (`analysis/ver_b.png`) reorders them to w, x, y, z with `[3:7] <- [6, 3, 4, 5]`. In `ver_a.png` the robot is tipped over on its side. In `ver_b.png` it stands upright with both feet near the floor. Only the reordered version is correct, which confirms that the CSV stores the rotation as x, y, z, w
8. **Full motion:** `play_motion.py` applies the reorder to every row and renders all 150 frames at 30 fps, with the camera following the pelvis. In the video the robot walks and kicks with the right leg
