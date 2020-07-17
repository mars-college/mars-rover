# Camera Setup on Jetson Nano

## Parts

### 2x PICAM360-CAMPT8MP

* [PICAM360-CAMPT8MP](https://store.picam360.com/#!/PICAM360-CAMPT8MP/p/87584243/category=0)
* [Resources](https://www.picam360.com/equipment/list)
	* [Getting Started](https://docs.google.com/document/d/e/2PACX-1vSMt4QLMU5Fcnl1lEDRx3El2-qZmblbb5lZ-JeDf8rnvXtTIgAwRqyoV3BF6YdZeB2WDPRZSCeysYS1/pub?embedded=true)
	* **[Install from the repo instructions](https://github.com/picam360/picam360-capture/issues)**
	
#### Notes:

* running `$ cmake .` alerted me to a missing dependency: `libjpeg`, which meant I needed to install `libjpeg-dev`... things they don't tell you in school...

* Figured it'd be a snap to test with the python_bindings provided in the repo. ran `$ python3 setup.py clean built install`, then `$ python3 test.py`. Was missing the package `traitlets`, installed with `$ pip3 isntall traitlets`. Seemed to work... until I can to a

### 2x Wide Angle Lens for Jetson Nano

* [SainSmart IMX219 Camera Module for NVIDIA Jetson Nano Board & Raspberry PI CM3 8MP Sensor 200 Degree FoV ](https://www.amazon.com/SainSmart-IMX219-Camera-Module-Raspberry/dp/B07WR87J2W/)

Resources:

* [Jetson Nano + Raspberry Pi Camera](https://www.jetsonhacks.com/2019/04/02/jetson-nano-raspberry-pi-camera/)
* [Jetson Nano B01 - Dual RPi Cameras + how to get faster frame rates](https://www.youtube.com/watch?v=GQ3drRllX3I)