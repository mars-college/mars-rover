# Locomotion

Making the Jetson Nano move the TR-08 tank platform.

## Hardware

* Jetson Nano - configured and ready to go.
* TB6612 breakout board from Adafruit [TB6612 Datasheet](resources/TB6612FNG_datasheet_en_20121101.pdf)
* Power source: 2x 3.7V 3400mAh Li-Ion cells in series for 7.4V.
* TR-08 tank platform with included motors.

## Tools

* Soldering Iron and supplies
* Wire clippers and strippers
* Header pins or sockets
* A breadboard
* Jumper wires compatible with the breadboard and header pins/sockets

## Software

These should already be installed on the Nano.

* Python3
* Jetson.GPIO

## Hardware Pre-flight

* Assemble the TR-08 tank platform
* Assemble and connect TB6612 breakout board.
* Setup Nano PWM pins
* Solder any necessary connections to allow easy and secure insertion into/onto breadboard or header sockets/pins.

### Assemble TR-08 Tank Platform

See instructions provided with the kit.

### Assemble and Connect TB6612 Breakout

1. Solder header pins and insert into a breadboard.
1. Use jumpers to connect `GND` pins to the `-` terminal of the power supply.
1. Connect the `+` terminal of the power supply to the `VM` pin of the breakout board.
1. Connect the remaining pins ass follows:

```
TB6612		NANO J41	OTHER
------		--------	-----
AIN1		TBD
AIN2		TBD
BIN1		TBD
BIN2		TBD
MOTORA(1)	--			MOTORA+
MOTORA(2)	--			MOTORA-
MOTORB(1)	--			MOTORB+
MOTORB(2)	--			MOTORB-
STANDBY		TBD
```

## Setup Nano PWM Pins

By default, the Nano does not come pre-configured for access to the PWM pins via `Jetson.GPIO`. A guide is provided for making the necessary changes. It's summarized below.

### Requirements:

* An NVIDIA Developers account
* A Windows machine or other way to run Microsoft Excel. (VM should work)
* A Linux machine. (VM should work)


### On the windows machine

1. Sign up for an NVIDIA Developers account.
1. Login to your NVIDIA Developers account.
1. Download the [pinmux spreadsheet](https://developer.nvidia.com/jetson-nano-pinmux)
1. Open on a Windows machine with Excel.
1. Locate **GPIO_PE06** (row 32) and change column **AS** (Customer Range) to **PM3_PWM2**, click OK and change column **AT** (Pin Direction) to **Output**, set column **AU** to **Int PD**.
1. Locate **LED_BL_PWM** (row 121) and change column **AS** to **PM3_PWM0**, click OK and change column **AT** to **Output**, set column **AU** to **Int PD**.
1. Click the big **Generate DT File** button at the top of the sheet.
1. Export the spreadsheet and save as a .csv, comma delimited, utf-8 (you *must* select this manually from the pullown menu) file to `jetson-nano-sd.csv`

### On the Linux Machine
1. `$ sudo apt-get update; sudo apt-get install build-essential bc bzip2 xz-utils git-core vim-common device-tree-compiler`
1. `$ cd /opt`
1. download the toolchain: `$ wget http://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-linux-gnu/gcc-linaro-7.3.1-2018.05-i686_aarch64-linux-gnu.tar.xz`
1. extract: `$ tar -xvf gcc-linaro-7.3.1-2018.05-i686_aarch64-linux-gnu.tar.xz` 
1. download the L4T Drivers: `$ wget https://developer.nvidia.com/embedded/L4T/r32_Release_v4.2/t210ref_release_aarch64/Tegra210_Linux_R32.4.2_aarch64.tbz2` or download the latest from [here](https://developer.nvidia.com/embedded/linux-tegra)
1. `$ tar -xvf Tegra210_Linux_R32.4.2_aarch64.tbz2`
1. `$ cd Linux_for_Tegra`
1. `$ ./sources_synch.sh`
1. use the tag `tegra-l4t-r32.4.2` when prompted. If you get any errors, run the script again. I was having server issues so this part took a lot of trial and error until the source servers were functional.
1. `$ cd /opt`
1. `$ git clone https://github.com/NVIDIA/tegra-pinmux-scripts.git`
1. `$ cd tegra-pinmux-scripts`
1. `$ mkdir csv`
1. copy the `jetson-nano-sd.csv` into the newly created csv: `$ cp <path-to-csv>/jetson-nano-sd.csv csv/p3450-porg.csv`
1. `$ ./csv-to-board.py p3450-porg`
1. `$ ./board-to-uboot.py p3450-porg > pinmux-config-p3450-porg.h`
1. `$ cd ../Linux_for_Tegra/sources/u-boot`
1. `$ cp ../../../tegra-pinmux-scripts/pinmux-config-p3450-porg.h board/nvidia/p3450-porg/`
1. `$ export CROSS_COMPILE=/opt/gcc-linaro-7.3.1-2018.05-i686_aarch64-linux-gnu/bin/aarch64-linux-gnu-`
1. `$ make distclean`
1. `$ make p3450-porg_defconfig`
1. `$ make`
1. `$ cp u-boot.bin ../../bootloader/t210ref/p3450-porg/`