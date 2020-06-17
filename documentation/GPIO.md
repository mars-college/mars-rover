# Locomotion

Making the Jetson Nano move the TR-08 tank platform.

## Hardware

* Jetson Nano - configured and ready to go.
* TB6612 breakout board from Adafruit [TB6612 Datasheet](resources/TB6612FNG_datasheet_en_20121101.pdf)
* Power source: 2x 3.7V 3400mAh Li-Ion cells in series for 7.4V.
* [4.5-28V to 0.8V-20V DC Buck converter](https://www.amazon.com/gp/product/B01MQGMOKI/)
* [SR-08 tank platform](https://www.amazon.com/gp/product/B07JPL6MHR/) with included motors.

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

By default, the Nano does not come pre-configured for access to the PWM pins via `Jetson.GPIO`. [A guide](resources/customizing_the_jetson_nano_40-pin_expansion_header_v1.2.pdf) is provided for making the necessary changes. It's summarized below.

### Requirements:

* Successful setup of the Jetson Nano with the ability to connect over ssh from the Linux host
* An NVIDIA Developers account
* A Windows machine or other way to run Microsoft Excel. (VM should work)
* A Linux machine. (VM should work)


### On the windows machine

1. Sign up and/or Login to your NVIDIA Developers account.
1. Download and open the [pinmux spreadsheet](https://developer.nvidia.com/jetson-nano-pinmux) in Excel.
1. *Enable Macros*
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

### On the Jetson Nano

1. `$ cat /proc/device-tree/nvidia,dtsfilename`

```
/dvs/git/dirty/git-master_linux/kernel/kernel-4.9/arch/arm64/boot/dts/../../../../../../hardware/nvidia/platform/t210/porg/kernel-dts/tegra210-p3448-0000-p3449-0000-b00.dts
```

1. Make note (copy somewhere) the `nano-dt-version` as specified by the last 3 characters preceeding the `.dts` extension. `b00` in the example above.
1. `$ sudo shutdown -h now`
1. Disconnect power
1. Locate J40 and connect pins 3 and 4 with a jumper to to activate Force Recovery mode.
1. ...connect to Linux host using micro USB cable?
1. ...power on?

## On the Linux Machine

1. `$ cd /opt/Linux_for_Tegra/sources/hardware/nvidia/platform/t210/porg/kernel-dts/porg-platforms/`
1. `$ cp <path-to-new-dt-files>/tegra210-jetson-nano-sd-pinmux.dtsi tegra210-porg-pinmux-p3448-0000-<nano-dt-version>.dtsi`
1. ` $ cp <path-to-new-dt-files>/tegra210-jetson-nano-sd-gpio-default.dtsi tegra210-porg-gpio-p3448-0000-<nano-dt-version>.dtsi`
1. `$ export CROSS_COMPILE=/opt/gcc-linaro-7.3.1-2018.05-i686_aarch64-linux-gnu/bin/aarch64-linux-gnu-`
1. `$ cd /opt/Linux_for_Tegra/sources/kernel/kernel-4.9/`1. `$ make ARCH=arm64 tegra_defconfig`1. `$ make ARCH=arm64 dtbs`
1. `$ cp arch/arm64/boot/dts/tegra210-p3448-0000-p3449-0000-b00.dtb ../../../kernel/dtb/`

## Flash the Jetson Nano

Be sure to setup your Jetson Nano for flashing. The [guide](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-322/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Fflashing.html%23) has a lot of extraneous info for this scenario. I found this [forum post](https://forums.developer.nvidia.com/t/how-to-put-nvidia-jetson-nano-in-force-recovery-mode/80400) to be both helpful (and disturbing).

### Double Check:

* You've activated the barrel connector for the external power source (set the jumper on J48).
* The Jetson is powered off.
* With power disconnected, connect to your Linux host via the Nano's USB Micro port to a USB port on the host.
* For models B00, look for J40 underneath the compute module. Connect the `FC REC` pin to `GND` with a jumper.
* Power up the Jetson by connecting power to the barrel connector.
* Remove the jumper from the `FC REC` and `GND` pins.

### On the Linux Host:

1. Confirm that the board is in recovery mode ([hint](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-322/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Fquick_start.html%23wwpID0E0TB0HA))
	* `$ lsusb` should return something like: `Bus 001 Device 004: ID 0955:7f21 NVIDIA Corp. APX` 
1. `$ sudo ./flash.sh jetson-nano-qspi-sd mmcblk0p1`