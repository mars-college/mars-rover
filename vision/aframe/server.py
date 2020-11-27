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

ROOT = os.path.dirname(__file__)
pcs = set()


# just for testing rotation params with mouse
import pyautogui



class DualFishEyeToEquirectangularStreamer(VideoStreamTrack):

    def __init__(self, camera_id):
        super().__init__()
        self.video, self.audio = True, False
        self.cap = cv2.VideoCapture(camera_id)
        self.width, self.height = 1280, 720
        self.setup_gl()

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
        self.prog['FOV'].value = 3.14159265358979
        self.prog['CAMERA_COEFF'].value = 0.88175


    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()

        if not ret:
            return
    
        self.tex = self.ctx.texture((
            self.width, self.height), 
            components=3, 
            data=frame.tobytes()
        )

        x, y = pyautogui.position()[0], pyautogui.position()[1]
        self.prog['yaw'].value = float(x-800+00)/400.0
        self.prog['pitch'].value = float(y-800+00)/500.0
        self.prog['roll'].value = float(y-800+00)/600.0

        self.tex.use()
        self.ctx.clear(1.0, 1.0, 1.0)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.ctx.buffer(self.vertices), 'in_vert')
        self.vao.render(mode=6)

        img_buf = Image.frombytes('RGB', (self.width, self.height), self.fbo.read(components=3))
        image_out = np.array(img_buf.convert('RGB'))

        new_frame = VideoFrame.from_ndarray(image_out, format="bgr24")
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
