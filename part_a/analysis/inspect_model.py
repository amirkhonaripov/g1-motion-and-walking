import sys
import mujoco

model = mujoco.MjModel.from_xml_path(sys.argv[1])
print("nq:", model.nq)

for i in range(model.njnt):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, i)
    print(i, name, "index:", model.jnt_qposadr[i])
