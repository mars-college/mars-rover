#!/bin/bash

# Install files and scripts for simcom_wwan@.service

PRE_SCRIPT_FILE="wwan_preup.sh"
POST_SCRIPT_FILE="wwan_postdown.sh"
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

echo "[+] Copying $PRE_SCRIPT_FILE to $SCRIPT_PATH"
cp "./$PRE_SCRIPT_FILE" "$SCRIPT_PATH"

echo "[+] Copying $POST_SCRIPT_FILE to $SCRIPT_PATH"
cp "./$POST_SCRIPT_FILE" "$SCRIPT_PATH"

echo "[+] Copying $SERVICE_FILE to $SERVICE_PATH"
cp "./$SERVICE_FILE" "$SERVICE_PATH"

echo "[+] Reloading systemd manager configuration"
systemctl daemon-reload
echo "[+] Successfully installed $SERVICE_FILE!"
echo "[+] To start, run: $ sudo systemctl start simcom_wwan@$IFACE.service"