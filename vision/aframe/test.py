import cv2
import numpy as np
import sys
import pyautogui
import time

from av import VideoFrame
import moderngl
from PIL import Image



# setup camera
idx = sys.argv[1]
video_capture = cv2.VideoCapture(int(idx))
#video_capture = cv2.VideoCapture("nvarguscamerasrc sensor_id=0 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")

width, height = 1280, 640

# setup gl
vertices = np.array([-1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0], dtype='f4')
ctx = moderngl.create_context(standalone=True)
fbo = ctx.simple_framebuffer((width, height), components=3)
fbo.use()
prog = ctx.program(
    vertex_shader=open('equirectangular.vert', 'r').read(),
    fragment_shader=open('equirectangular.frag', 'r').read()
)

# display
#cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
#cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)


while True:

    ret, frame = video_capture.read()
    if ret is False:
        continue

    print('frame shape', frame.shape)


    # mouse    
    x, y = pyautogui.position()[0], pyautogui.position()[1]    
    #prog['ang1'].value = float(x)/800.0
    
    prog['ay1'].value = float(x-800+800)/300.0
    prog['ap1'].value = float(y-800+800)/300.0
    prog['ar1'].value = float(y-800+800)/300.0

    h, w = frame.shape[0:2]

    tex = ctx.texture((w, h), 
        components=3, 
        data=frame.tobytes()
    )

    tex.use()
    ctx.clear(1.0, 1.0, 1.0)
    vao = ctx.simple_vertex_array(prog, ctx.buffer(vertices), 'in_vert')
    vao.render(mode=6)

    img_buf = Image.frombytes('RGB', (width, height), fbo.read(components=3))
    frame = cv2.resize(frame, (width, height))
    frame = np.array(img_buf.convert('RGB'))

    if frame is not None:
        # Perform any pre-processing of frame before stabilization here
        pass


    if ret:
        cv2.imshow('window', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.1)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()


