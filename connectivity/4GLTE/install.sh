#!/bin/bash

# Install files and scripts for simcom_wwan@.service

SCRIPT_FILE="wwan_preup.sh"
SCRIPT_PATH="/etc/simcom_wwan"
SERVICE_PATH="/lib/systemd/system"
SERVICE_FILE="simcom_wwan@.service"
IFACE="wwan0"
SERVICE="simcom_wwan@$IFACE.service"

if [ "$EUID" -ne 0 ]
  then echo "[!] Please run as root"
  exit 1
fi

if [[ -d "$SCRIPT_PATH" ]]; then
	echo "[-] $SCRIPT_PATH already exists"
else
	echo "[+] Creating directory $SCRIPT_PATH"
	mkdir "$SCRIPT_PATH"
fi

echo "[+] Copying wann_preup.sh to $SCRIPT_PATH"
cp "./$SCRIPT_FILE" "$SCRIPT_PATH"
echo "[+] Copying $SERVICE_FILE to $SERVICE_PATH"
cp "./$SERVICE_FILE" "$SERVICE_PATH"

echo "[+] Reloading systemd manager configuration"
systemctl daemon-reload
echo "[+] Successfully installed $SERVICE_FILE!"
echo "[+] To start, run: $ sudo systemctl start $SERVICE_FILE"