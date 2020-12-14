# Programming an Arduino Nano over USB on Jetson Nano

Yes, you can program an Arduino from the CLI in Linux. This kinda just touches on the steps:

* Connect Hardware
* Install tools
* Configure
* Compile and Upload

Why are we doing this? Because I bought the cheapo MPU6050 thinking it was a good idea. Seems like all the best libraries for it are for Arduino. So while we wait for the "better" boards to get here, I decided to hack together a way to Frankenstein all the pieces together: MPU6050 via i2c > Arduino via USB serial > Jetson Nano. If the "better" boards a re truly better, then we can ditch the Arduino, but I have a sneaking suspicion that the Arduino might be here to stay...

## Connect Hardware

* Arduino Nano Clone with CH341G USB chipset
* Jetson Nano B0

1. Use a USB micro cable to connect the Arduino Nano Clone to the Jetson Nano.
1. Run `dmesg` and look for:

```
[333663.719873] usb 1-2.4: new full-speed USB device number 7 using tegra-xusb
[333663.743305] usb 1-2.4: New USB device found, idVendor=1a86, idProduct=7523
[333663.743362] usb 1-2.4: New USB device strings: Mfr=0, Product=2, SerialNumber=0
[333663.743402] usb 1-2.4: Product: USB2.0-Serial
[333663.749997] ch341 1-2.4:1.0: ch341-uart converter detected
[333663.752242] usb 1-2.4: ch341-uart converter now attached to ttyUSB5
```

1. Luckily, the `ch341-uart` module came pre-installed. The Arduino Nano was assigned to `/dev/ttyUSB5`. If `dmesg` doesn't show the device being recognized, diconnect and reconnect. If you still don't see anything, you need to install the CH341 drivers, see [these instructions](https://learn.sparkfun.com/tutorials/how-to-install-ch340-drivers/linux) (yuck).

## Install tools

1. `sudo apt-get install python3-serial arduino-mk` --source: [https://github.com/sudar/Arduino-Makefile](https://github.com/sudar/Arduino-Makefile)

## Configure

1. Head to the Blink example `cd usr/share/doc/arduino-mk/examples/Blink`... yes we're going to do the most basic AVR "hello world".
1. Modify the `Makefile` with `sudo nano Makefile` so that the following configuration is set (everything else commented out): 
  
```
BOARD_TAG   = uno
ARDUINO_DIR = /usr/share/arduino
MONITOR_PORT= /dev/<REPLACE_WITH_YOUR_ttyUSB*>
include /usr/share/arduino/Arduino.mk
```

Note: change <REPLACE_WITH_YOUR_ttyUSB\*> to the ttyUSB\* you found when checking `dmesg`. I' get to the `BOARD_TAG = uno` thing in a sec.

## Compile and Upload

1. Prepare `sudo make clean`
1. Upload `sudo make upload`

If it all worked out, then you have a blinking Arduino Nano programmable from your Jetson Nano. Word.

## Caveats
   
Note: Yes, after a short trial and error period, I noticed the `do_upload` generating the wrong `avrdude` parameters. After compiling, I tried changing board and baud settings manually and settled on a command that worked:

```
sudo /usr/share/arduino/hardware/tools/avr/../avrdude -q -V -p atmega328p -C /usr/share/arduino/hardware/tools/avr/../avrdude.conf -D -c arduino -b 115200 -P /dev/ttyUSB5 -U flash:w:build-nano-atmega328/Blink.hex:i
```
I luckily stumbled upon the place where you can how avrdude arguments are selected: `/usr/share/arduino/hardware/arduino/boards.txt`. The `uno` description had all the right settings.
