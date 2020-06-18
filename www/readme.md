## Web control interface

This webpage (rover.html) is meant to be hosted on a Raspberry Pi; it should show a stream from the picam and give you an interface to control the pi rover over t'internet. 

### Raspbery Pi setup
- connect to the internet. static-ip prefered. 
- install `webiopi` and `mjpg-streamer` (see webcam section for more on installing)

### Control configs

Buttons are bound to the functions (fwd, rev, spin) defined at the end of `rover.js`. Change GPIO pin number and command as fit.

### Webcam stream 

In general follow [This blog post](https://medium.com/@sandeeparneja/streaming-images-from-raspberrypi-to-an-html-website-77802e5cedee).

Change this line (line 18) in `rover.html` by adding the streaming url as src. Should be something like:

`<img id="imagestream" src='http://192.168.178.57:9000/?action=stream'/>`