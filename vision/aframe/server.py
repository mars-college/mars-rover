import argparse
import asyncio
import json
import logging
import os
import platform
import ssl

import numpy as np
from PIL import Image
import cv2
from av import VideoFrame
import moderngl

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer

PI = 3.14159265358979
ROOT = os.path.dirname(__file__)
pcs = set()

# camera parameters / constants
cam1_radius = (1.0, 1.1)      # camera #1 multiply radius 
cam2_radius = (1.0, 1.1)      # camera #2 multiply radius 
cam1_margin = (0.107, 0.079)  # camera #1 trim sides
cam2_margin = (0.081, 0.099)  # camera #2 trim sides
width, height = 3264, 2464    # camera resolution
output_size = (1920, 960)     # stream output size
fov = 200.0                   # camera field of view in degrees


class DualFishEyeToEquirectangularStreamer(VideoStreamTrack):

    def __init__(self, camera_id):
        super().__init__()
        self.video = True 
        self.audio = False
        self.width = width
        self.height = height
        self.output_size = output_size
        self.cap1 = cv2.VideoCapture("nvarguscamerasrc sensor_id=0 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")
        self.cap2 = cv2.VideoCapture("nvarguscamerasrc sensor_id=1 ! video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")
        self.setup_gl()


    def exit(self):
        # this is not called yet
        self.cap1.release()
        self.cap2.release()
        self.tex1.release()
        self.tex2.release()
        cv2.destroyAllWindows()


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


    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # read cameras
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()

        if not ret1 and not ret2:
            return

        self.tex1.write(data=frame1)
        self.tex2.write(data=frame2)

        # update rotation parameters
        self.prog['yaw'].value = 0.0
        self.prog['pitch'].value = 0.0
        self.prog['roll'].value = 0.0

        # render
        self.ctx.clear(1.0, 1.0, 1.0)
        self.vao.render(mode=6)
        self.fbo.read_into(self.frame, components=3)

        # output
        final_frame = np.array(Image.fromarray(self.frame.astype(np.uint8)).resize(self.output_size))
        new_frame = VideoFrame.from_ndarray(final_frame, format="bgr24")
        new_frame.pts = pts
        new_frame.time_base = time_base

        return new_frame


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def client_script(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def aframejs(request):
    content = open(os.path.join(ROOT, "aframe.min.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    pc = RTCPeerConnection()
    pcs.add(pc)
            
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)
            
    player = DualFishEyeToEquirectangularStreamer(args.camera_id)

    await pc.setRemoteDescription(offer)
    for t in pc.getTransceivers():
        if t.kind == "audio" and player.audio:
            pc.addTrack(player.audio)
        elif t.kind == "video" and player.video:
            pc.addTrack(player) #player.video
    
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )

async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC webcam demo")
    parser.add_argument("--camera_id", type=int, default=0, help="Index of camera device")
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        print('set logging')
        logging.basicConfig(level=logging.DEBUG)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", client_script)
    app.router.add_get("/aframe.min.js", aframejs)    
    app.router.add_post("/offer", offer)
    
    web.run_app(app, host=args.host, port=args.port, ssl_context=ssl_context)
