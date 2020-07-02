# WiFi with the PAU05 USB adapter

Setting up WiFi connectivity with the PAU05 2.4GHz 300mbps USB WiFi Adapter on the Jetson Nano B01. This guide assumes that you've already successfully setup the Jetson Nano to run headless and that you can log in over `ssh`.

### Parts

* PAU05 2.4GHz 300mbps USB WiFi Adapter

The adapter works with the Jetson Nano B01 without the need to install

### Additional Resources

Sources and additional guides in case this isn't cutting it ;)

* [Jetson Nano USB Headless WiFi Setup](https://desertbot.io/blog/jetson-nano-usb-headless-wifi-setup-edimax-ew-7811un)
* [Setting up a WIFI connection via command line on Debian/Ubuntu (Network Manager)](https://www.96boards.org/documentation/consumer/guides/wifi_commandline.md.html)

## Setup Hardware

1. Connect the PAU05 adapter to the Jetson Nano. Simple.

## Pre-Flight

* Make sure to update and upgrade your installed packages: `$ sudo apt-get update && sudo apt-get full-upgrade -y`

Some commands to give you more insight into your WiFi hardware and RF environment.

* `$ lsusb` - List info on your USB wifi adapter
* `$ nmcli device wifi list` - List info on your wifi signal
* `$ nmcli connection show` - List connections
* `$ iwconfig` - List info your your wifi connections
* `$ ifconfig wlan0` - List info about the wlan0 wifi connection

## Process (Using `nmcli`)

1. Create a saved connection.`$ sudo nmcli connection add con-name <connection_alias> ifname wlan0 type wifi ssid <network_name>`.
1. Configure for wpa pre-shared key authentication: `$ sudo nmcli connection modify <connection_alias> wifi-sec.key-mgmt wpa-psk`
1. Set the password: `$ sudo nmcli connection modify <connection_alias> wifi-sec.psk <password>`
1. Clear the password from your bash session history: `$ history -cw`
1. Turn off power saving mode for stability: `$ sudo iw dev wlan0 set power_save off`
1. Connect: `$ nmcli connection up <connection_alias>`