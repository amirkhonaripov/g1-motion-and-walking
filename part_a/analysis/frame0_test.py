import sys
import mujoco
import numpy as np
import imageio

csv_read = np.loadtxt(sys.argv[1], delimiter=",")
model = mujoco.MjModel.from_xml_path(sys.argv[2])
data = mujoco.MjData(model)

print(data.qpos)
print(data.qpos.shape)
print(data.qpos[3:7])


ver_a = csv_read[0].copy()

ver_b = csv_read[0].copy()
ver_b[3:7] = ver_b[[6, 3, 4, 5]]

print(ver_a)
print(ver_b)

data.qpos[:] = ver_a
mujoco.mj_forward(model, data)

renderer = mujoco.Renderer(model, height=480, width=640)

cam = mujoco.MjvCamera()
cam.lookat[:] = ver_a[:3]
cam.distance = 3
cam.azimuth = 90
cam.elevation = -15

renderer.update_scene(data, camera=cam)

image = renderer.render()
imageio.imwrite("ver_a.png", image)

data.qpos[:] = ver_b
mujoco.mj_forward(model, data)

renderer.update_scene(data, camera=cam)

image = renderer.render()
imageio.imwrite("ver_b.png", image)
