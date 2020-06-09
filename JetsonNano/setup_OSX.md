# Setting Up Jetson Nano with OSX

A quick step-by-step guide to getting the Jetson Nano setup to run *headless* over an ethernet ssh connection.

This guide assumes some familiarity with setting up Single Board Computers like the RaspberryPi or BeagleBone.

Please visit official the [Getting Started With Jetson Nano Developer Kit](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) guide if you get stuck.
 

## Overview

### Parts

* Jetson Nano B01
* 5v 4A Powersupply
* 16GB or larger microSD card
* MicroSD card adapter/reader
* USB A to USB micro data cable

### Software

* screen (should come pre-installed on OSX)
* [balenaEtcher](https://www.balena.io/etcher/#download)
* [Jetson Nano Developer Kit SD Card Image](https://developer.nvidia.com/jetson-nano-sd-card-image)

## Process

### Prepare the SD Card

1. Download and install [balenaEtcher](https://www.balena.io/etcher/#download)
1. Download the Jetson Nano [image file](https://developer.nvidia.com/jetson-nano-sd-card-image).
1. Insert the microSD card into an adapter or reader and insert into your computer.
1. Flash the microSD card using balenaEtcher:
	1. Click *Select image* and select the image .zip file
	1. Click *Select target* and choose the MicroSD card
	1. Click *Flash!* and wait for balenaEtcher to write and verify the image.

### Prepare the Hardware
	
1. Insert the flashed MicroSD card into the Jetson Nano.
1. Connect the Jetson Nano to your computer using the USB A to Micro USB connector.
1. Connect the Nano to your network using the ethernet connection. 
1. Position a jumper across the J48 connector to use power from the 5.5mm x 2.1mm Barrel Jack Connector. It's located on the developer board near the barrel connector. The jumper is supplied but connected to only one of the J48 pins.

### Connecting over USB

1. Open a terminal window.
1. Run `$ ls -/dev/ | grep tty.usbmodem` and make note of existing devices.
1. Connect power to the Jetson Nano and wait a couple of minutes.
1. Run `$ ls -/dev/ | grep tty.usbmodem` again and look for a new device with the format `tty.usbmodem<some unique number>`
1. Run `$ screen /dev/tty.usbmodem<unique number>` to start your console session in your terminal window.
1. Setup the Jetson Nano by following the steps on screen:
	1. Accept the agreement
	2. Set language
	3. Set location by country/region
	4. Set your timezone
	5. Select *YES* for UTC clock
	6. Set account name
	7. Set username
	8. Set user password
	9. Confirm passowrd
	10. Select `eth0` to setup network configuration over ethernet.
	11. Use DHCP if you don't already have a reserved IP address. Hint: you don't need to be connected to the network yet.
	12. Set the hostname for the Nano
	13. Log in from the console once configuration finishes.
	14. Run `$ ip a s eth0`
	15. Copy the IP address (`inet`) and MAC address (`link/ether`)
1. In a new terminal window run `ssh <your_username>@<your_nano_ip_address>` and enter yes.
1. Log into the Nano using your user's password.
1. If connected to the internet, go ahead and update your installed packages by running `$ sudo apt-get update; sudo full-upgrade -y`
1. Reboot `$ sudo reboot`

### Setup a reserved static IP

To make sure the nano appears at the same IP address each time it connects to your network (e.g. after rebooting), reserve a static IP address on your router for its MAC address.

1. Make sure you have admin access to your router or have your network admin assist.
1. Locate the DHCP Reserved IP settings for your router. Each router is different and may place these settings under "Static IP" assignment or something else.
1. Set an IP address for the Nano within the same subnet as your router's DHCP server.
1. Enter the MAC address of the Nano.
1. Enter any other info your router may require.
1. Save the settings and reboot the Nano.

### Passwordless Entry

1. Copy your host machine's ssh keys over to the Nano: `$ ssh-copy-id <your_username>@<your_nano_ip_address>`
1. Enter the password for your Nano user.
1. Run `$ ssh <your_username>@<your_nano_ip_address>` to log in.

Optionally, you can setup an alias for your device.

1. Add the following lines to `~/.ssh/config`

```
Host <pick_an_alias>
        HostName <nano_ip_address>
        User <nano_username>
        IdentityFile ~/.ssh/id_rsa
```

### Helpful Packages

It'll come in handy to install the following packages:

* `apt-utils`
* `nvidia-jetpack`

## Additional Tips

The Jetson has two power profiles, called modes. Mode 0 is 10W, Mode 1 is 5W. 

* To set the mode to 5 Watt mode: `$ sudo nvpmodel -m 1`
* To set it back to 10 Watt mode: `$ sudo nvpmodel -m 0`

### `rsynch`

To copy and synchronize files on your local machine with the Nano, use `rsynch`.

* `$ rsync -r <source_path> <user>@<remote>:<destination_path>`