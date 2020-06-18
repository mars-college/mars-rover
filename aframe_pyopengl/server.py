import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid

import cv2
from aiohttp import web
from av import VideoFrame

from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder


import numpy as np
from PIL import Image
import moderngl
import cv2


#cap = cv2.VideoCapture(1)






ROOT = os.path.dirname(__file__)
print("ROOT IS!", ROOT)

logger = logging.getLogger("pc")
pcs = set()






class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform
        self.init_gl()


        
    def init_gl(self):
        print("initialize gl")
        print('gl5')
        self.width, self.height = 640, 360
        print('gl6')
        self.ctx = moderngl.create_context(standalone=True) #, backend='egl')
        self.fbo = self.ctx.simple_framebuffer((self.width, self.height), components=3)
        self.fbo.use()
        print('gl7')
        
        self.vertices = np.array([
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
            -1.0, 1.0,
        ], dtype='f4')

        print('gl8')
        
        self.prog = self.ctx.program(
            vertex_shader="""
                #version 330

                in vec2 in_vert;
                out vec2 pos;

                void main() {
                    pos = 0.5*(1.0+in_vert);
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330

                uniform sampler2D textureObj;
                in vec2 pos;
                out vec4 f_color;

                #ifdef GL_ES
                precision mediump float;
                precision mediump int;
                #endif

                #define PI 3.14159265358979
                #define _THETA_S_Y_SCALE	(640.0 / 720.0)

                //uniform vec4 uvOffset;

                void main() {
                    vec4 uvOffset = vec4(0);
                    float radius = 0.445;

                    vec2 revUV = pos.xy;
                    if (pos.x <= 0.5) {
                        revUV.x = revUV.x * 2.0;
                    } else {
                        revUV.x = (revUV.x - 0.5) * 2.0;
                    }
                    
                    revUV *= PI;

                    vec3 p = vec3(cos(revUV.x), cos(revUV.y), sin(revUV.x));
                    p.xz *= sqrt(1.0 - p.y * p.y);

                    float r = 1.0 - asin(p.z) / (PI / 2.0);
                    vec2 st = vec2(p.y, p.x);

                    st *= r / sqrt(1.0 - p.z * p.z);
                    st *= radius;
                    st += 0.5;
                    
                    if (pos.x <= 0.5) {
                        st.x *= 0.5;
                        st.x += 0.5;
                        st.y = 1.0 - st.y;
                        st.xy += uvOffset.wz;
                    } else {
                        st.x = 1.0 - st.x;
                        st.x *= 0.5;
                        st.xy += uvOffset.yx;
                    }
                    
                    st.y = st.y * _THETA_S_Y_SCALE;
                    f_color = vec4(texture(textureObj, st).rgb, 1.0);
                }
            """
        )
        self.idx=1
        print('gl9')
        import time
        time.sleep(5)
        

                


    async def recv(self):
        frame = await self.track.recv()
        self.transform = 'equirectangular'
        img = frame.to_ndarray(format="bgr24")
        print(img.shape)
        print('r1')
        #ret, frame = await cap.read()
        print('r2')
        
        #if not ret:
        #    return None
        print('r3')
        
        self.tex = self.ctx.texture((
            self.width, self.height), 
            components=3, 
            data=img.tobytes())
        print('r4')
        
        self.tex.use()
        print('r5')
        self.ctx.clear(1.0, 1.0, 1.0)
        print('r6')
        vao = self.ctx.simple_vertex_array(self.prog, self.ctx.buffer(self.vertices), 'in_vert')
        print('r7')
        # vao.render(mode=moderngl.TRIANGLES)
        print('r8')
        vao.render(mode=6)
        print('r9')
        
        image = Image.frombytes('RGB', (self.width, self.height), self.fbo.read(components=3)).convert('RGBA')
        print('r10')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image.save('triangle%03d.png'%self.idx, format='png')
        print('r11')
        
        #print('typesss',image_out.shape, image_out.dtype, type(image_out))
        print()
        image_out = np.array(image.convert('RGB'))

        new_frame = VideoFrame.from_ndarray(image_out, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        print('r12')
        

        self.idx+=1
        return new_frame


    async def recv_old(self):
        
        
        frame = await self.track.recv()
        self.transform = 'equirectangular'
        #self.transform = 'rotate'

        if self.transform == "cartoon":
            img = frame.to_ndarray(format="bgr24")

            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "rotate":
            # rotate image
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

            # rebuild a VideoFrame, preserving timing information
            print('types', img.shape, img.dtype, type(img))

            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == 'equirectangular':
            #print('getting back frame')

            img = frame.to_ndarray(format="bgr24")
            print(img.shape, img.dtype)
            pil_img = Image.fromarray(img).convert('RGB')
            pil_img_data = np.fromstring(pil_img.tobytes(), np.uint8)
        
            glTexImage2D(GL_TEXTURE_2D, 0, 3, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, pil_img_data)

            glDrawArrays(GL_QUADS, 0, 4)


            #

            # PNG
            # Read the data and create the image
            
            image_buffer = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
            image_out = np.frombuffer(image_buffer, dtype=np.uint8)
            image_out = image_out.reshape(self.height, self.width, 4)
            image_out = np.array(Image.fromarray(image_out).convert('RGB'))
            imgP = Image.fromarray(image_out, 'RGB')
            imgP.save(r"image_outd%03d.png"%self.idx_frame)
            self.idx_frame+=1
            #types (540, 960, 3) uint8 <class 'numpy.ndarray'>
            #types (360, 640, 4) uint8 <class 'numpy.ndarray'>
            print('typesss',image_out.shape, image_out.dtype, type(image_out))
            new_frame = VideoFrame.from_ndarray(image_out, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base


            return new_frame
        else:
            return frame


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def aframejs(request):
    content = open(os.path.join(ROOT, "aframe-master.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    params = await request.json()
    print('params',params.keys())
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    if args.write_audio:
        recorder = MediaRecorder(args.write_audio)
    else:
        recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        if track.kind == "audio":
            pc.addTrack(player.audio)
            recorder.addTrack(track)
        elif track.kind == "video":
            local_video = VideoTransformTrack(
                track, transform=params["video_transform"]
            )
            pc.addTrack(local_video)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        }),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebRTC audio / video / data-channels demo"
    )
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host for HTTP server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    parser.add_argument("--write-audio", help="Write received audio to a file")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/aframe-master.js", aframejs)   
    app.router.add_post("/offer", offer)
    web.run_app(
        app, 
        access_log=None, 
        host=args.host, 
        port=args.port, 
        ssl_context=ssl_context
    )
