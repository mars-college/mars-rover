import time
from PIL import Image
import cv2
import numpy as np
import moderngl

# parameters / constants
PI = 3.14159265358979
cam1_radius = (1.0, 1.1)      # camera #1 multiply radius 
cam2_radius = (1.0, 1.1)      # camera #2 multiply radius 
cam1_margin = (0.107, 0.079)  # camera #1 trim sides
cam2_margin = (0.081, 0.099)  # camera #2 trim sides
width, height = 3264, 2464    # camera resolution
fov = 200.0                   # camera field of view in degrees

# setup camera
cam1 = cv2.VideoCapture("nvarguscamerasrc sensor_id=0 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")
cam2 = cv2.VideoCapture("nvarguscamerasrc sensor_id=1 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")

# setup gl
vertices = np.array([-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0], dtype='f4')
ctx = moderngl.create_context(standalone=True, backend='egl')
fbo = ctx.simple_framebuffer((width, height), components=3)
fbo.use()
prog = ctx.program(
    vertex_shader=open('equirectangular.vert', 'r').read(),
    fragment_shader=open('equirectangular.frag', 'r').read()
)

# set constants
prog['FOV'].value = PI * fov / 180.0
prog['cam1_radius'].value = cam1_radius
prog['cam2_radius'].value = cam2_radius
prog['cam1_margin'].value = cam1_margin
prog['cam2_margin'].value = cam2_margin
prog['yaw'].value = 0.0
prog['pitch'].value = 0.0
prog['roll'].value = 0.0
prog['camTex1'].value = 0
prog['camTex2'].value = 1

# setup textures
tex1 = ctx.texture((width, height), components=3)
tex2 = ctx.texture((width, height), components=3)
tex1.use(prog['camTex1'].value)
tex2.use(prog['camTex2'].value)


vao = ctx.simple_vertex_array(prog, ctx.buffer(vertices), 'in_vert')

frame = np.empty((height, width, 3), dtype='u1')

# for calculating FPS
frame_count = 0
t0 = time.time()

# rotation parameters
yaw = 0 
pitch = 0
roll = 0


while True:

    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()

    if not ret1 or not ret2:
        continue
    
    tex1.write(data=frame1)
    tex2.write(data=frame2)

    yaw += 0.0072
    pitch += 0.0065
    roll += 0.0069

    prog['yaw'].value = yaw
    prog['pitch'].value = pitch
    prog['roll'].value = roll

    ctx.clear(1.0, 1.0, 1.0)
    vao.render(mode=6)
    fbo.read_into(frame, components=3)

    # display
    disp_frame = np.array(Image.fromarray(frame.astype(np.uint8)).resize((1280, 720)))
    cv2.imshow('window', disp_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_count += 1
    print('fps', frame_count / (time.time() - t0))

# clean-up
cam1.release()
cam2.release()
tex1.release()
tex2.release()
cv2.destroyAllWindows()


