# SSL Certificate creation

Last thing we want is to use unencrypted communication. Anyone can sniff the network traffic and have full plain text view of data, including login credentials. In order to setup a secure https server, you'll need to generate ssl certificates from a key.

This guide walks through the basics of creating a self-signed certificate.

### Use-case scenarios

* running an https server on the Jetson Nano
* securing WebRTC streams

This method is for development environments only. Production environments require a certificate signed by a Certified Authority (CA). Using a self-signed certificate will result in browser warnings. Scary stuff for the average user.

## Generating

### Assumptions:

* Your host system is OSX or Linux

### Requirements:

* OpenSSL

### Downloading:

* Using [homebrew](https://brew.sh) (for OSX folks): `$ brew install openssl`
* Using apt-get (for Debian and Ubuntu Linux users): `$ sudo apt-get upgrade && sudo apt-get install openssl -y` 

### Make Key then Certificate

1. Generate the Key: `$ openssl genrsa 2048 > host.key`
1. Modify the Permissions: `$ chmod 400 host.key`
1. Create Certificate from the Key`$ openssl req -new -x509 -nodes -sha256 -days 365 -key host.key -out host.cert`
1. Copy to the [appropriate directories](https://www.getpagespeed.com/server-setup/ssl-directory). Use the full path to them in server configuration files.