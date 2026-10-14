## How to get circular motion
`legged_gym/envs/base/legged_robot_config.py` lists four commands by default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading. The policy receives the first three (forward speed, sideways speed, turning rate), heading is only used in training.
The `deploy/deploy_mujoco/deploy_mujoco.py` reads those commands from the `cmd_init` line of `deploy/deploy_mujoco/configs/g1.yaml` into `cmd`, a list of three values (`[0.5, 0, 0]` by default).
In the `g1.yaml`, I changed the third cmd_init value to 0.5:

```diff
- cmd_init: [0.5, 0, 0]
+ cmd_init: [0.5, 0, 0.5]
```

The robot started circling left. It walks forward at 0.5 m/s and turns at 0.5 rad/s at the same time, so its direction keeps rotating while it moves and the path bends into a circle. The values are inside the range the policy was trained on (`[-1, 1]`), and the sign sets the direction.

## Policy input
The policy receives an observation of 47 numbers every 10 physics steps (control decimation):
1. base angular velocity (3) - from MuJoCo (`d.qvel[3:6]`)
2. gravity orientation (3) - computed from the base quaternion (`d.qpos[3:7]`)
3. command (3) - `cmd_init` from `g1.yaml`
4. joint angles minus the default angles (12) - from MuJoCo (`d.qpos[7:]`)
5. joint velocities (12) - from MuJoCo (`d.qvel[6:]`)
6. previous action (12) - the policy's own last output
7. sin and cos of the gait phase (2) - computed from the simulation time

The angular velocity, joint angles, joint velocities and command are multiplied by the scales from `g1.yaml` to stay in the range of inputs the policy was trained on

## Policy output and how it's converted into torques
The policy outputs 12 numbers (`deploy_mujoco.py` stores them in `action`), one for each leg joint (`num_actions`). They are converted into torques in two steps:
1. target angles: `action * action_scale + default_angles` (`action_scale` = 0.25 in `g1.yaml`)
2. `pd_control` turns each target angle into a torque: `(target angle - current angle) * kp + (0 - current joint velocity) * kd`, with `kp`s and `kd`s from `g1.yaml`


