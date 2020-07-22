# Wireguard on Jetson Nano

This guide will walk through setting up wireguard on the Jetson Nano. 

### Use Case

* You want to remotely access your Jetson Nano securely. Wherever you are, wherever it is.
* You have a server with a static IP address.
* You and the Nano are both set up as clients on the VPN server.
* Maybe you have multiple Nanos you want to admin remotely?

```
You > Server < Nano
---\ Wireguard /---
---/  Tunnel   \---
```

In this scenario, it's presumed that neither you, nor your Nano will have a static or predictable IP address. If that's not the case, whichever device has the static IP should be configured as the server and the other device can connect to it as a client. Once you've both connected to the remote server via the VPN, you'll be able to `ssh` into the Nano using its hostname and VPN ip address. For Example:

```
VPN IP Subnet: 10.10.0.0/24
Server VPN IP Address: 10.10.0.1
Nano VPN IP Address: 10.10.0.2
Your VPN IP Address: 10.10.0.3
```

Login would look something like this, assuming both devices were connected to the VPN:

```
$ ssh NanoHostName@10.10.0.2
```

### Overview of the Steps

1. Install
	1. Wireguard Tools via `apt-get` 
	1. Wireguard kernel module by compiling on Jetson Nano
1. Configure
1. Connect

## Install Wireguard Tools

Adapted from the installation steps published on the wireguard homepage available [here](https://www.wireguard.com/install/).

* Note: This will not install the kernel module, which is necessary for creating the wireguard interface.

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

When you log back in, run `sudo wg;echo $?`. You should get an exit code `0`, which means the tool installation succeeded!

## Install Kernel Module

Adapted from the [guide](https://www.wireguard.com/compilation/) on the official site.

1. Clone the kernel module source: `$ git clone https://git.zx2c4.com/wireguard-linux-compat`
1. Install the toolchain: `$ sudo apt-get install libelf-dev build-essential pkg-config`
1. Compile: `$ make -C wireguard-linux-compat/src -j$(nproc)`
1. Install: `$ sudo make -C wireguard-linux-compat/src install`
1. Install: `$ sudo modprobe -v wireguard`
1. Check: `$ lsmod | grep wireguard`

## Configure

* Note: The server is where your client's IP address is set. If the configuration file on your client doesn't have the corresponding IP address, the connection will still be established, but all packets to and from the client will be dropped.

### Both Client + Server

1. Change to your home directory: `$ cd`
1. Make a folder named `.wg`: `$ mkdir .wg`
1. Change directories to `.wg`: `$ cd .wg`
1. Prevent other users from accessing the keys: `$ umask 077`
1. Generate the public and private keys: `$ wg genkey | tee privatekey | wg pubkey > publickey`
 
### Server (Static IP)

1. `$ sudo nano /etc/wireguard/wg0.conf`

```
[Interface]
# Name = Server
Address = <VPN_LOCAL_IP_ADDRESS>/<SUBNET>
ListenPort = <LISTENING_PORT>
PrivateKey = <server private key DO NOT EVER SHARE EVER!!!>

[Peer]
#Name = Client
PublicKey = <host's public key SHARE WITH SERVER ADMIN FOR ACCESS>
AllowedIPs = <SERVER_ADMIN_ASSIGNED_VPN_LOCAL_IP_ADDRESS>/32
PersistentKeepalive = 20
```

### Client (You and your Nano)

1. `$ sudo nano /etc/wireguard/wg0.conf`

```
[Interface]
# Name = Client
Address = <SERVER_ADMIN_ASSIGNED_VPN_LOCAL_IP_ADDRESS>/32
PrivateKey = <based64 private key DO NOT EVER SHARE EVER!!!>

[Peer]
#Name = Server
Endpoint = <SERVER_IP_ADDRESS>:<SERVER_LISTENING_PORT>
PublicKey = <base64 public key ASK SERVER ADMIN FOR ACCESS>
AllowedIPs = <VPN_IP_SUBNET>/<MASK>
PersistentKeepalive = 20
```

## Connect

### Server first, then client(s)

1. `$ sudo wg-quick wg0 up`
1. `$ sudo wg`

### Enabling @ Boot

1. `$ sudo systemctl enable wg-quick@wg0.service`

### Login using `ssh`

* It's highly recommended to use key based authentication only

#### Client to Client

Server to Client? Skip to the second step.

1. Test the connection to server: `$ ping -c 5 <SERVER_VPN_IP_ADDRESS>`
1. Test the connection to other client: `$ ping -c 5 <CLIENT_VPN_IP_ADDRESS>`
1. Login to the other client: `$ ssh <USER>@<CLIENT_VPN_IP_ADDRESS>`