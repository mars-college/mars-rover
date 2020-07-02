# Wireguard on Jetson Nano

This guide will walk through setting up wireguard on the Jetson Nano.

### Overview of the Steps

1. Install
1. Configure
1. Connect

## Install

Adapted from the installation steps published on the wireguard homepage available [here](https://www.wireguard.com/install/).

1. `$ sudo add-apt-repository ppa:wireguard/wireguard`
1. `$ sudo apt-get update`
1. `$ sudo apt-get install wireguard`

You may have seen an error like this:

```
Processing triggers for flash-kernel (3.98ubuntu11~18.04.1) ...
Unsupported platform.
dpkg: error processing package flash-kernel (--configure):
 installed flash-kernel package post-installation script subprocess returned error exit status 1
Errors were encountered while processing:
 flash-kernel
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

It seems that `flash-kernel` isn't necessary. So simply remove it to prevent further issues:

1. `$ sudo apt-get remove flash-kernel`
1. `$ sudo reboot`

When you log back in, run `sudo wg;echo $?`. You should get an exit code `0`, which means the installation succeeded!

## Configure

### Both Client + Server

1. Change to your home directory: `$ cd`
1. Make a folder named `.wg`: `$ mkdir .wg`
1. Change directories to `.wg`: `$ cd .wg`
1. Generate the public and private keys:
 
### Server

1. `$ sudo nano /etc/wireguard/wg0.conf`

```
```

### Client 

1. `$ sudo nano /etc/wireguard/wg0.conf`

```
```

## Connect

### Server

1. `$ sudo wg-quick wg0 up`
1. `$ sudo wg`

### Client

1. `$ sudo wg-quick wg0 up`
1. `$ sudo wg`