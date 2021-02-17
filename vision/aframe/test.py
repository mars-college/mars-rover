import time
import argparse
import asyncio
import threading
import json
import logging
import os
import platform
import ssl
import io
import base64

from gstreamer import *
import numpy as np
import moderngl
from PIL import Image

import tornado
import tornado.ioloop
import tornado.web
import tornado.websocket

import cv2

PI = 3.14159265358979
ROOT = os.path.dirname(__file__)
pcs = set()

# camera parameters / constants
cam1_radius = (1.0, 1.1)      # camera #1 multiply radius 
cam2_radius = (1.0, 1.1)      # camera #2 multiply radius 
cam1_margin = (0.075, 0.1)    # camera #1 trim sides
cam2_margin = (0.09, 0.075)   # camera #2 trim sides
width, height = 2048, 1024    # camera resolution
stream_width, stream_height = 3264, 2464
output_size = (1632,1232)     # stream output size
fps = 12
fov = 200.0                   # camera field of view in degrees

# test parameters
view_raw = False


# setup camera
caps_filter = 'capsfilter caps=video/x-raw(memory:NVMM),format=NV12,width={},height={},framerate={}/1'.format(stream_width, stream_height, fps)
command1 = 'nvarguscamerasrc sensor_id=1  ! {} ! nvvidconv ! video/x-raw, format=RGBA ! videoscale ! video/x-raw, width={},height={} ! appsink emit-signals=True sync=false'.format( caps_filter, width, height)
command2 = 'nvarguscamerasrc sensor_id=0  ! {} ! nvvidconv ! video/x-raw, format=RGBA ! videoscale ! video/x-raw, width={},height={} ! appsink emit-signals=True sync=false'.format( caps_filter, width, height)

# setup gl
if platform.system() == "Darwin":
    ctx = moderngl.create_context(standalone=True)
else:
    ctx = moderngl.create_context(standalone=True, backend='egl')

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

# setup vertex array and frame buffer
vao = ctx.simple_vertex_array(prog, ctx.buffer(vertices), 'in_vert')
frame = np.empty((height, width, 3), dtype='u1')


# for calculating FPS
frame_count = 0
t0 = time.time()

# rotation parameters
yaw = 0 
pitch = 0
roll = 0



# main camera loop
with GstVideoSource(command1) as pipeline1, GstVideoSource(command2) as pipeline2:
    
    while True:
        # read cameras
        buffer1 = pipeline1.pop()
        buffer2 = pipeline2.pop()

        frame1 = np.ascontiguousarray(buffer1.data[:,:,:3])
        frame2 = np.ascontiguousarray(buffer2.data[:,:,:3])

        print("received frames", frame1.shape, frame2.shape, frame1.dtype)

        tex1.write(data=frame1)
        tex2.write(data=frame2)

        # update rotation parameters
        prog['yaw'].value = yaw
        prog['pitch'].value = pitch
        prog['roll'].value = roll

        # render
        ctx.clear(1.0, 1.0, 1.0)
        vao.render(mode=6)
        fbo.read_into(frame, components=3)

        # display
        if frame_count % 15 == 0:
            if view_raw:
                frame_full = np.array(Image.fromarray(np.concatenate([frame1, frame2], axis=1)).resize((1200, 540)))
                cv2.imshow("window", np.flipud(frame_full))
            else:
                frame_full = np.array(Image.fromarray(frame).resize((1440, 720)))
                cv2.imshow("window", frame_full)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # fps
        frame_count += 1
        elapsed = time.time() - t0
        print(' -> fps', frame_count / elapsed)
        if elapsed > 10:
            break


# clean-up
#buffer1.release()
#buffer2.release()
tex1.release()
tex2.release()
cv2.destroyAllWindows()


