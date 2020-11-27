import cv2
import numpy as np
import sys
import pyautogui
import time

from av import VideoFrame
import moderngl
from PIL import Image

# setup camera
width, height = 1280, 640
idx = sys.argv[1]
video_capture = cv2.VideoCapture(int(idx))
#video_capture = cv2.VideoCapture("nvarguscamerasrc sensor_id=0 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")

# setup gl
vertices = np.array([-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0], dtype='f4')
ctx = moderngl.create_context(standalone=True)
fbo = ctx.simple_framebuffer((width, height), components=3)
fbo.use()
prog = ctx.program(
    vertex_shader=open('equirectangular.vert', 'r').read(),
    fragment_shader=open('equirectangular.frag', 'r').read()
)

# set constants
prog['FOV'].value = 3.14159265358979
prog['CAMERA_COEFF'].value = 0.88175

# display
#cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

import time

frames = 0
t_0 = time.time()

time.sleep(1)
ret, frame = video_capture.read()

while True:
    t0 = time.time()

    ret, frame = video_capture.read()
    if ret is False:
        continue

    t1 = time.time()

    print('frame shape', frame.shape)

    # set rotation uniforms with mouse    
    x, y = pyautogui.position()[0], pyautogui.position()[1]    
    prog['yaw'].value = float(x-800+00)/400.0
    prog['pitch'].value = float(y-800+00)/500.0
    prog['roll'].value = float(y-800+00)/600.0

    t2 = time.time()

    h, w = frame.shape[0:2]
    tex = ctx.texture((w, h), 
        components=3, 
        data=frame.tobytes()
    )

    tex.use()
    t3 = time.time()
    ctx.clear(1.0, 1.0, 1.0)
    t4 = time.time()
    vao = ctx.simple_vertex_array(prog, ctx.buffer(vertices), 'in_vert')
    t5 = time.time()
    vao.render(mode=6)

    t6 = time.time()

    img_buf = Image.frombytes('RGB', (width, height), fbo.read(components=3))
    # frame = cv2.resize(frame, (width, height))
    frame = np.array(img_buf.convert('RGB'))
    t7 = time.time()

    if ret:
        cv2.imshow('window', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    t8 = time.time()
    t_all = t8-t0

    nframes+=1
    fps = float(nframes)/(time.time()-t_0)

    print('fps=%0.2f : %0.5f, %0.5f, %0.5f, %0.5f, %0.5f, %0.5f, %0.5f, %0.5f' % (fps, (t1-t0)/t_all, (t2-t1)/t_all, (t3-t2)/t_all, (t4-t3)/t_all, (t5-t4)/t_all, (t6-t5)/t_all, (t7-t6)/t_all, (t8-t7)/t_all))

    # time.sleep(0.1)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()


