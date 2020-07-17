# Example of serving up PiCam in a web browser on JetsonNano using Flask

* Code lifted from: [Using Jetson Nano and a Raspberry Pi Camera for Video Streaming](https://maker.pro/nvidia-jetson/tutorial/streaming-real-time-video-from-rpi-camera-to-browser-on-jetson-nano-with-flask)

1. Install dependencies `$ sudo apt-get install python3-opencv python3-flask`
1. Run the server: `$ python3 server.py`
1. Open your browser and point it to: `http://<your_nano_IP>:8080`

* more nvidia GStreamer stuff [here](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3231/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Faccelerated_gstreamer.html%23wwpID0E0OQ0HA)