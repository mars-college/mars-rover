# Javascript Remote Control of Robotic Tank Platform over WebSockets

This walkthrough covers steps to setting up remote control of a Mountain Ark SR-08 robotic tank platform with a Raspberry Pi over WebSockets.

Hardware setup is not covered in detail.

## Assumptions

* Your host system is running OSX, though this should work on  Windows and Linux as well.
* A basic working knowledge of Linux CLI, Raspberry Pi, Python.
* You've clones this repository locally.
* Nice to have but not necessary to know JavaScript, WebSockets, Python, HTML.
* Experience prototyping electronics enough to know how to setup a breadboard to handle two different voltages.

## Requirements

To reproduce the project in its entirety, you'll need to have access to an electronics workbench/lab, outfit with a few basic tools in addition to having purchased the necessary hardware.

### Tools

* Soldering Iron and supplies
* Wire clippers and strippers
* Header pins or sockets
* A breadboard
* Jumper wires compatible with the breadboard and header pins/sockets
* Multimeter (for checking voltages and 
* Oscilloscope for debugging hardware and connections (optional).

### Hardware

* Raspberry Pi (Zero W used) - configured and ready to go.
* [TB6612 breakout board from Adafruit](https://www.adafruit.com/product/2448) - [TB6612 Datasheet](resources/TB6612FNG_datasheet_en_20121101.pdf)
* 2x 3.7V 18650 Li-Ion cells.
* [4.5-28V to 0.8V-20V DC Buck converter](https://www.amazon.com/gp/product/B01MQGMOKI/)
* [SR-08 tank platform](https://www.amazon.com/gp/product/B07JPL6MHR/) with included motors.

### Software

* Raspberry Pi accessible over SSH on a local network
* Python3
* pigpio GPIO control application for Raspberry Pi
* tornado python web server framework

## Hardware Pre-flight

* Make sure your Raspberry Pi is configured to connect to your WiFi network and that you can SSH into it.
* Assemble the TR-08 tank platform.
* Determine which voltage rails will carry regulated +5V and which will be connected directly to the LI battery pack.
* Assemble and connect [TB6612 breakout board](https://www.adafruit.com/product/2448).
* Solder any necessary connections to allow easy and secure insertion into/onto breadboard or header sockets/pins.
* The Raspberry Pi used is powered from a Micro USB connection. I've cut and prepared a Micro USB power cable to be inserted into a breadboard.

### Assemble TR-08 Tank Platform

Follow the instructions provided in their [video](https://www.youtube.com/watch?v=wATykzn6Z34).

### Setting up Power Connections

* Charge your LI batteries fully before proceeding.

LI battery cells have an operating range from ~8V - ~6.5V. This needs to be regulated down to 5V for the Raspberry Pi and the TB6612 board. A Buck Converter board is used to achieve this. 

* Do not place batteries into the compartment until you are ready to adjusts the voltage output on the buck converter!

The idea is that you will set your breadboard up with on rail as carrying the direct connection to the LI battery pack and the other will carry the regulated 5V.

The Raspberry Pi is powered over a Micro USB connection. For this project, I cut an existing cable and fitted the wires with header pins for easy insertion into a breadboard.

1. Solder header pins to your [4.5-28V to 0.8V-20V DC Buck converter](https://www.amazon.com/gp/product/B01MQGMOKI/) and insert into breadboard.
1. Connect the `V+ in` and `GND in` of the Buck Converter to the voltage rails on the side of the breadboard which will connect to the LI batteries.
1. Connect the `V+ out` and `GND out` of the Buck Converter to the voltage rails on side of the breadboard which will carry the regulated 5V.
1. Connect the LI battery to the appropriate voltage rail on your breadboard.
1. Insert fully charged LI cells into the battery compartment.
1. Using a multimeter and a small screw driver, adjust the output of the buck converter until it reads between +5.0 to 5.1 volts.
1. Disconnect the LI batteries.
1. Insert a prepare Micro USB cable into the breadboard (you'll have to cut and solder appropriate connections (like header pins)

### Assemble and Connect TB6612 Breakout

1. Solder header pins and insert into a breadboard.
1. Use jumpers to connect `GND` pins to the breadboard rail you've setup as common ground.
1. Connect the `VCC` pin of the breakout board to the breadboard rail you've setup as the `+5V` connection to your LI battery pack. 
1. Connect the `VM` pin of the breakout board to the breadboard rail you've setup as the `+` connection to your LI battery pack.
1. Connect the remaining pins using [this diagram](https://pinout.xyz/) as follows:

```
TB6612		RPi GPIO	OTHER
------		--------	-----
GND 		GPIO 34
PWMA		BCM 12
PWMB		BCM 13
AIN1		BCM 4
AIN2		BCM 17
BIN1		BCM 27
BIN2		BCM 22
MOTORA(1)	--			MOTORA+
MOTORA(2)	--			MOTORA-
MOTORB(1)	--			MOTORB+
MOTORB(2)	--			MOTORB-
STANDBY		TBD
```

### Install Software on Raspberry Pi

Complete the following steps while connected to the Raspberry Pi over WiFi via ssh. It's recommended that you do this is the Raspberry Pi plugged into a AC adapter instead of the LI battery pack.

1. `$ sudo apt-get update; sudo apt-get upgrade -y`
1. `$ sudo apt-get install pigpio pigpiod python3-pigpio`
1. `$ sudo apt-get install python3-tornado` 
1. `$ sudo shutdown -h now`

Disconnect from the AC adapter and connect to the power connector on the platform (Micro USB you inserted into the breadboard)

## Testing WebSockets Locally

To test locally on your host, you'll need to make sure that you have tornado installed.

1. `$ pip3 install tornado`
1. `$ cd <repository_root_path>/WebApp`
1. `$ python3 server-test-local.py`
1. In a web browser with JavaScript and WebSockets enabled, navigate to `http://localhost:80`
1. Check that the `WebSocket status:` reads `connected`.
1. Interact with the GUI and check to console for messages received.

## Controlling the Robot!

You'll need to power the Raspberry Pi from the LI battery pack now and locate the robot to a place where it can move freely but still maintain WiFi connectivity.

### Start `pigpiod` on the RPi

The `pigpio` library runs a separate service that manages communication with the GPIO pins. You need to start the `pigpiod` service first.

1. `$ sudo pigpio`

Optionally, you can have this start up automatically on boot up.

1. `$ sudo systemctl enable pigpiod`
1. `$ sudo systemctl restart pigpiod`


### Fire up the HTTP server on the RPi

1. `$ cd <repository_root_path>/WebApp`
1. `$ python3 server.py`

Optionally install and manage as a `systemd` service, `rover.service` using `install.sh`, `uninstall.sh`, `update.sh` scripts:

1. `$ sudo bash install.sh`

* start the server: `sudo systemctl start rover.service`
* stop the server: `sudo systemctl stop rover.service`
* restart the server: `$ sudo systemctl restart rover.service`
* enable startup on boot: `sudo systemctl enable reover.service`
* disable startup on boot: `sudo systemctl disable reover.service`

### Access the control interface on your host machine

1. Make sure you know the IP address of your Raspberry Pi: `$ ifconfig wlan0`
1. Open a browser on your host (make sure you have JavaScript enabled!) and navigate to: `http://<your_pi_IP_Address>:80`
1. Check the WebSocket status in the bottom and make sure it reads `connected`. If not, open the WebConsole (Firefox) and look for errors.

The joystick GUI element should now move the robot around!