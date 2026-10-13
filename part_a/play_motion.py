import sys
import mujoco
import numpy as np
import imageio

csv_read = np.loadtxt(sys.argv[1], delimiter=",")
model = mujoco.MjModel.from_xml_path(sys.argv[2])
data = mujoco.MjData(model)

csv_adjusted = csv_read.copy()
csv_adjusted[:, 3:7] = csv_read[:, [6, 3, 4, 5]]

fps = 30

renderer = mujoco.Renderer(model, height=480, width=640)

cam = mujoco.MjvCamera()
cam.distance = 3
cam.azimuth = 90
cam.elevation = -15

with imageio.get_writer("motion.mp4", fps=fps) as writer:
    for row in csv_adjusted:
        data.qpos[:] = row
        mujoco.mj_forward(model, data)
    
        cam.lookat[:] = row[:3]

        renderer.update_scene(data, camera=cam)
        image = renderer.render()
        
        writer.append_data(image)

