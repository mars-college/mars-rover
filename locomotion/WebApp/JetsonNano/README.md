# Remote Control of Robotic Tank Platform over WebSockets (Jetson Nano)

### WARNING: Currently Untested! It's *mostly* complete, but not yet verified. Proceed at your own risk!

This walkthrough covers steps to setting up remote control of a Mountain Ark SR-08 robotic tank platform with a Jetson Nano over WebSockets on a local WiFi network.

Some hardware setup is not covered in detail.

## Assumptions

* Your host system is running OSX, though this should work on  Windows and Linux as well.
* A basic working knowledge of Linux CLI, Arduino, Jetson Nano, Python.
* You've cloned this repository locally.
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
* Shrink Tube + Lighter (optional)
* [USBtinyISP](http://www.gikfun.com/various-electronic-modules-c-68/usbtinyisp-usbtiny-isp-programmer-bootloader-avr-w-usb-6-pin-p-133.html) or some other ISP compatible with Arduino and ATTiny85

### Hardware/Parts

* 2x [ATTiny85](https://www.mouser.com/productdetail/microchip-technology-atmel/attiny85-20pu?qs=8jWQYweyg6NCiiaOb5GI9Q%3D%3D)
* Jetson Nano Development Kit B01 - [setup](https://www.jetsonhacks.com/2019/08/21/jetson-nano-headless-setup/) and ready to go.
	* able to login over `ssh`?
	* [8265AC/8265NGW Wireless NIC Module](https://www.amazon.com/gp/product/B07X2NLL85) [installed](https://www.jetsonhacks.com/2019/04/08/jetson-nano-intel-wifi-and-bluetooth/) and able to connect to your local network?
* [TB67H420FTG Dual/Single Motor Driver](https://www.pololu.com/product/2999)
* 2x 3.7V 18650 Li-Ion cells.
* [5A DC-DC Adjustable Buck Converter 4~38v to 1.25-36v Step Down Power Supply](https://www.amazon.com/gp/product/B079N9BFZC/)
* [8x 3.7V 18650 Li-Ion cells](https://www.batteryjunction.com/lg-mh1-18650-3200mah-battery.html).
* [2x 18650 battery holders](https://www.amazon.com/gp/product/B06XSHT9HC/).
* 2x 5.5mm x 2.1mm plug with wires
* 1x 5.5mm x 2.1mm socket with wires
* [8-Bay Charger for Li-ion 18650 batteries](https://www.amazon.com/gp/product/B07ZSHFFHF/)
* [SR-08 tank platform](https://www.amazon.com/gp/product/B07JPL6MHR/) with included motors.
* 5V to 3.3V regulator

### Software

* Arduino IDE
	* ATTiny Boards Manager
	* TinyWire library
* Python3
* Jetson.GPIO - python wrapper for controlling J41 GPIO header pins
* `tornado` python web server framework

## Let's Built It!

### Assemble TR-08 Tank Platform

Follow the instructions provided in their [video](https://www.youtube.com/watch?v=wATykzn6Z34).

### Burning the ATTiny85s

1. Download and the Arduino IDE
1. Add this link to the "Additional Boards Manager URLs" in the Arduino Preferences: `https://raw.githubusercontent.com/damellis/attiny/ide-1.6.x-boards-manager/package_damellis_attiny_index.json`
1. Clone the TinyWire library into your `Arduino/libraries` folder: `git clone https://github.com/lucullusTheOnly/TinyWire.git` 
1. Maybe restart Arduino IDE?
1. In the "Tools" pulldown of the Arduino IDE, make the following selections:

```
Board: "ATTiny25/45/85"
Processor: "ATTiny85"
Clock: "Internal 16 MHz"
Programmer: "USBtinyISP
```

1. Connect the USBtinyISP to your host machine
1. Use wire jumpers (with header style pins) to connect the USBtinyISP 6-pin output to a breadboard in such a way that you can easily insert, program, and remove the ATTiny85s
1. Insert the first ATTiny85
1. Select "Burn Bootloader" from the "Tools" menu
1. Open `i2c_Slave.ino` in `/path_to_the_repo/mars-rover-main/locomotion/Arduino/`
1. Change the `ADDRESS` to `0x10` for the left motor
1. Press the "Upload" button.
1. Remove and label the ATTiny85: "L"
1. Insert the second ATTiny85
1. Change the `ADDRESS` to `0x11` for the right motor
1. Press the "Upload" button.
1. Remove and label the ATTiny85: "R"

***WARNING***: You cannot use `i2cdetect` to confirm the ATTiny85s are connected to the Jetson Nano. Due to some issue I've still not wrapped my head around, doing so will cause the SDA lines to drive low and not return high until the MCUs are reset (power cycled). Use an oscilloscope to verify connectivity via the PWM outputs.

### Setting up Power Connections

#### 1. Prepare the Breadboard

* Use pre-cut, solid-core jumpers.
* Connect the `GND` rails of the breadboard with a jumper.
* Label your breadboard with one `+V` rail carrying `+5V` and the other `+3.3V`.

#### 2. Making the battery pack

* Charge your Li-ion batteries fully.

* The Li-ion battery pack is setup in a 4s2p configuration for a total of 12V @ ~7000mAh. It has an operating range from 12V - 16.8V. This needs to be regulated down to 5V for the Jetson Nano. A Buck Converter board is used to achieve this. 

* With the battery holders empty...

1. Strip the ends of the compartment wires
1. Strip the ends of the 5.5mm x 2.1mm plug with wires
1. Cut and slide shrink wrap over the wires
1. Twist and solder the +V wires together.
1. Twist and solder the GND wires together.
1. Use a multimeter to confirm connectivity from the battery holders to the 5.5mm x 2.1mm plug
1. Trim excess conductors, slide shrink tube over the joints, shrink to prevent shorting.

* Once charged, place the batteries into the compartment and test voltage with a multimeter. You should get ~16.5V

#### 3. Setting up the Step Down Converter

* The step-down voltage converter will be used only to supply the Jetson Nano with 5V with a max of 5A.

* The Jetson Nano is powered over a 5.5mm x 2.1mm barrel connection. For this project, I cut an existing cable and fitted the wires with header pins for easy insertion into a breadboard.

1. Solder the `+V` and `GND` **output** of the step down converter to a 5.5mm x 2.1mm **plug**. 
1. **DO NOT PLUG INTO THE JETSON NANO YET**
1. Solder the `+V` and `GND` **input** of the step down converter to wires that can be inserted into the breadboard.
1. **DO NOT CONNECT THE STEP DOWN CONVERTER TO THE BREADBOARD YET**

* The LI battery pack connects directly to the Motor Driver. We'll set that up next.

#### 4. Setting up the Motor Driver

* The Motor Driver has terminal blocks for +VM and each motor.

1. Solder provided terminal blocks (on the top) and header pins (pointed down) to the [TB67H420FTG Dual/Single Motor Driver](https://www.pololu.com/product/2999) and insert into the breadboard.
1. Use jumpers to connect the Motor Driver `VCC` (+V) pin to the `+5V` rail on the breadboard.
1. Use jumpers to connect the `GND` pins to the `GND` rail on the breadboard.
1. Connect the "LEFT" motor to the `MOTORA` terminal block (match + with red, - with black)
1. Connect the "RIGHT" motor to the `MOTORB` terminal block (match + with red, - with black)
1. Connect a 5.5mm x 2.1mm jack to the `VM` terminal block on the Motor Driver.
1. Double check your connections.

#### 5. Powering the breadboard rails

1. Plug the battery pack into the +VM jack.
1. Use a multimeter to measure +5V on the `VCC` output of the Motor Driver.
1. Place the 3.3V regulator on the breadboard and connect its `VIN` to `+5V`, it's `GND` to `GND` and measure +3.3V on its output. Use jumpers.

#### 6. Adjusting Step Down Converter

1. Connect the `+V IN` wire of the Step Down Converter to the `VM` of the Motor Driver on the breadboard
1. Connect the `GND IN` wire of the Step Down Converter to the `GND` rail of the breadboard.
1. Use a multimeter to measure the voltage at the output of the Step Down Converter.
1. Use a precision flat head screw driver to adjust the voltage until it's ~5.125V

#### 7. Connect the ATtiny85s

1. Insert the ATTiny85s into the breadboard and use jumpers to connect them to the `+3.3V` and `GND` rails.
1. Use jumpers to connect their `SDA` and `SCL` pins together for form SDA and SCL I2C "busses"
1. Connect the SDA bus to pin 3 of the Jetson Nano J-41 40-pin header.
1. Connect the SCL bus to pin 5 of the Jetson Nano J-41 40-pin header.
1. Connect `pin 6` of the "LEFT" ATTiny85 to the `PWMA` pin on the Motor Driver.
1. Connect `pin 1` of the "LEFT" ATTiny85 to the `AIN1` pin on the Motor Driver.
1. Connect `pin 2` of the "LEFT" ATTiny85 to the `AIN2` pin on the Motor Driver.
1. Connect `pin 6` of the "RIGHT" ATTiny85 to the `PWMB` pin on the Motor Driver.
1. Connect `pin 1` of the "RIGHT" ATTiny85 to the `AIN1` pin on the Motor Driver.
1. Connect `pin 2` of the "RIGHT" ATTiny85 to the `AIN2` pin on the Motor Driver.

### Secure Parts to the Platform

* No specific placement suggestions just yet
* Zip-ties help
* Pay attention to where your connections need to be made
* Move things around before you lock them down

### Install Software on Jetson Nano

Complete the following steps while connected to the Jetson Nano over WiFi via ssh. It's recommended that you do this with the Nano plugged into a AC adapter instead of the Li-ion battery pack.

1. `$ sudo apt-get update; sudo apt-get upgrade -y`
1. `$ sudo apt-get install python3-tornado` 
1. `$ sudo shutdown -h now`

Disconnect from the AC adapter and connect to the power connector on the platform.

## Testing WebSockets Locally

To test locally on your host, you'll need to make sure that you have `tornado` installed.

1. `$ pip3 install tornado`
1. `$ cd <repository_root_path>/WebApp`
1. `$ python3 server-test-local.py`
1. In a web browser with JavaScript and WebSockets enabled, navigate to `http://localhost:80`
1. Check that the `WebSocket status:` reads `connected`.
1. Interact with the GUI and check to console for messages received.

## Controlling the Robot!

You'll need to power the Raspberry Pi from the Li-ion battery pack now and locate the robot to a place where it can move freely but still maintain WiFi connectivity.

### Fire up the HTTP server on the RPi

1. `$ cd <repository_root_path>/locomotion/WebApp`
1. `$ python3 server.py`

Optionally install and manage as a `systemd` service, `rover.service` using `install.sh`, `uninstall.sh`, `update.sh` scripts:

1. `$ sudo bash install.sh`

* start the server: `sudo systemctl start rover.service`
* stop the server: `sudo systemctl stop rover.service`
* restart the server: `$ sudo systemctl restart rover.service`
* enable startup on boot: `sudo systemctl enable rover.service`
* disable startup on boot: `sudo systemctl disable rover.service`

### Access the control interface on your host machine

1. Make sure you know the IP address of your Nano: `$ ifconfig wlan0`
1. Open a browser on your host (make sure you have JavaScript enabled!) and navigate to: `http://<your_pi_IP_Address>:80`
1. Check the WebSocket status in the bottom and make sure it reads `connected`. If not, open the WebConsole (Firefox) and look for errors.

The joystick GUI element should now move the robot around!