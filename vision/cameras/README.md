# Testing Cameras on the Jetson Nano

### Goals

Create a pipeline that streams a 360 camera feed to the web.

* open the available camera feeds from CSI and USB
* crop feeds to 1:1
* combine feed into dual fisheye
* convert dual fisheye to equirectangular
* create network accessible stream (TCP/UDP/RTSP/RTP/etc.)
* open the stream in a browser
* display the stream in VR mode 


## Research

* [Composite Two CSI Camera stream into single RTP stream](https://forums.developer.nvidia.com/t/composite-two-csi-camera-stream-into-single-rtp-stream/127402)
* [Linux Webcam Server](https://www.moreno.marzolla.name/software/linux-webcam-server/) - ancient but maybe useful?
*[How to Make Raspberry Pi Webcam Server and Stream Live Video || Motion + Webcam + Raspberry Pi](https://www.instructables.com/id/How-to-Make-Raspberry-Pi-Webcam-Server-and-Stream-/) - mentions `motion`, worth checking out.
* [flutter-webrtc-server](https://github.com/flutter-webrtc/flutter-webrtc-server)
* [uv4l-server](https://www.linux-projects.org/documentation/uv4l-server/)
* [How to Build a Video Call & Voice Chat App in WebRTC Using Javascript/node.js?](https://medium.com/hackernoon/how-to-build-a-video-call-voice-chat-app-in-webrtc-using-javascript-node-js-d256d434acbc)
* [GStreamer WebRTC: A flexible solution to web-based media](https://opensource.com/article/19/1/gstreamer)
* [WebRTC Native C++ to Browser Video Streaming Example](https://sourcey.com/articles/webrtc-native-to-browser-video-streaming-example)


## Trial and Error

1. `$ gst-launch-1.0 nvarguscamerasrc sensor_id=0 ! nvoverlaysink`

```
2020-07-16 22:16:06.317576: I tensorflow/stream_executor/platform/default/dso_loader.cc:48] Successfully opened dynamic library libcudart.so.10.2
Setting pipeline to PAUSED ...
Pipeline is live and does not need PREROLL ...
Setting pipeline to PLAYING ...
New clock: GstSystemClock
GST_ARGUS: Creating output stream
CONSUMER: Waiting until producer is connected...
GST_ARGUS: Available Sensor modes :
GST_ARGUS: 3264 x 2464 FR = 21.000000 fps Duration = 47619048 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

GST_ARGUS: 3264 x 1848 FR = 28.000001 fps Duration = 35714284 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

GST_ARGUS: 1920 x 1080 FR = 29.999999 fps Duration = 33333334 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

GST_ARGUS: 1280 x 720 FR = 59.999999 fps Duration = 16666667 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

GST_ARGUS: 1280 x 720 FR = 120.000005 fps Duration = 8333333 ; Analog Gain range min 1.000000, max 10.625000; Exposure Range min 13000, max 683709000;

GST_ARGUS: Running with following settings:
   Camera index = 0 
   Camera mode  = 2 
   Output Stream W = 1920 H = 1080 
   seconds to Run    = 0 
   Frame Rate = 29.999999 
GST_ARGUS: Setup Complete, Starting captures for 0 seconds
GST_ARGUS: Starting repeat capture requests.
CONSUMER: Producer has connected; continuing.
```
