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
fps = 12
fov = 200.0                   # camera field of view in degrees


class DualFishEyeToEquirectangularStreamer():

    def __init__(self, camera_id):
        super().__init__()
        self.video = True 
        self.audio = False
        self.stream_width = stream_width
        self.stream_height = stream_height
        self.width = width
        self.height = height
        self.fps = fps
        self.caps_filter = 'capsfilter caps=video/x-raw(memory:NVMM),format=NV12,width={},height={},framerate={}/1'.format(self.stream_width, self.stream_height, self.fps)
        self.command1 = 'nvarguscamerasrc sensor_id=1  ! {} ! nvvidconv ! video/x-raw, format=RGBA ! videoscale ! video/x-raw, width={},height={} ! appsink emit-signals=True sync=false'.format( self.caps_filter, self.width, self.height)
        self.command2 = 'nvarguscamerasrc sensor_id=0  ! {} ! nvvidconv ! video/x-raw, format=RGBA ! videoscale ! video/x-raw, width={},height={} ! appsink emit-signals=True sync=false'.format( self.caps_filter, self.width, self.height)
        
        self.new_frame = False     
        self.setup_gl()

        self.frame1 = None
        self.frame2 = None


    def exit(self):
        # this is not called yet
        self.tex1.release()
        self.tex2.release()


    def setup_gl(self):
        if platform.system() == "Darwin":
            self.ctx = moderngl.create_context(standalone=True)
        else:
            self.ctx = moderngl.create_context(standalone=True, backend='egl')

        self.fbo = self.ctx.simple_framebuffer((
            self.width, self.height), 
            components=3)
            
        self.fbo.use()
        
        self.vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
            -1.0, 1.0,
        ], dtype='f4')

        self.prog = self.ctx.program(
            vertex_shader=open('equirectangular.vert', 'r').read(),
            fragment_shader=open('equirectangular.frag', 'r').read()
        )

        # set constants
        self.prog['FOV'].value = PI * fov / 180.0
        self.prog['cam1_radius'].value = cam1_radius
        self.prog['cam2_radius'].value = cam2_radius
        self.prog['cam1_margin'].value = cam1_margin
        self.prog['cam2_margin'].value = cam2_margin
        self.prog['yaw'].value = 0.0
        self.prog['pitch'].value = 0.0
        self.prog['roll'].value = 0.0
        self.prog['camTex1'].value = 0
        self.prog['camTex2'].value = 1

        # setup textures
        self.tex1 = self.ctx.texture((self.width, self.height), components=3)
        self.tex2 = self.ctx.texture((self.width, self.height), components=3)
        self.tex1.use(self.prog['camTex1'].value)
        self.tex2.use(self.prog['camTex2'].value)

        # setup vertex array and frame buffer
        self.vao = self.ctx.simple_vertex_array(self.prog, self.ctx.buffer(self.vertices), 'in_vert')
        self.frame = np.empty((self.height, self.width, 3), dtype='u1')


    def recv(self):
        if self.new_frame:
            self.tex1.write(data=self.frame1)
            self.tex2.write(data=self.frame2)

            # update rotation parameters
            self.prog['yaw'].value = 0.0
            self.prog['pitch'].value = 0.0
            self.prog['roll'].value = 0.0

            # render
            self.ctx.clear(1.0, 1.0, 1.0)
            self.vao.render(mode=6)
            self.fbo.read_into(self.frame, components=3)

            # output
            self.new_frame = False
            return self.frame


def thread_function(obj):
    with GstVideoSource(obj.command1) as pipeline1, GstVideoSource(obj.command2) as pipeline2:
        while True:
            # read cameras
            buffer1 = pipeline1.pop()
            buffer2 = pipeline2.pop()
            obj.frame1 = np.ascontiguousarray(buffer1.data[:,:,:3])
            obj.frame2 = np.ascontiguousarray(buffer2.data[:,:,:3])
            obj.new_frame = True


class ImageWebSocket(tornado.websocket.WebSocketHandler):

    clients = set()
    
    def open(self):
        ImageWebSocket.clients.add(self)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        im = Image.fromarray(player.recv())
        buf = io.BytesIO()
        im.save(buf, format='JPEG')
        buf = base64.b64encode(buf.getvalue())
        self.write_message(buf)

    def on_close(self):
        ImageWebSocket.clients.remove(self)
        print("WebSocket closed from: " + self.request.remote_ip)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--camera_id", type=int, default=0, help="Index of camera device")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()
    player = DualFishEyeToEquirectangularStreamer(args.camera_id)

    if args.verbose:
        print('set logging')
        logging.basicConfig(level=logging.DEBUG)

    script_path = os.path.dirname(os.path.realpath(__file__))
    app = tornado.web.Application([
        (r"/websocket", ImageWebSocket),
        (r"/(.*)", tornado.web.StaticFileHandler, {'path': script_path, 'default_filename': 'index.html'})
        #(r"/(.*)", tornado.web.StaticFileHandler, {'path': script_path, 'default_filename': 'client2.js'}),
        #(r"/(.*)", tornado.web.StaticFileHandler, {'path': script_path, 'default_filename': 'aframe.min.js'}),
    ])       

#    http_server = tornado.httpserver.HTTPServer(app, ssl_options = {
#    "certfile": args.cert_file,
#    "keyfile": args.key_file,
#})

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(args.port, address=args.host)
    thread = threading.Thread(target=thread_function, args=(player,))
    print("thread Started")
    thread.start()
    print("Starting server: http://localhost:" + str(args.port) + "/")

    tornado.ioloop.IOLoop.current().start()


