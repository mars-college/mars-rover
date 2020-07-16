#!/bin/bash

# Uninstall files and scripts for simcom_wwan@.service

SCRIPT_PATH="/etc/simcom_wwan"
SERVICE_PATH="/lib/systemd/system"
SERVICE_FILE="simcom_wwan@.service"
IFACE="wwan0"
SERVICE="simcom_wwan@$IFACE.service"

if [ "$EUID" -ne 0 ]
  then echo "[!] Please run as root"
  exit 1
fi

echo "[+] Stopping $SERVICE_FILE"
systemctl stop "$SERVICE"
echo "[+] Disabling $SERVICE_FILE"
systemctl disable "$SERVICE"

if [[ -d "$SCRIPT_PATH" ]]; then
	echo "[+] Removing $SCRIPT_PATH"
	rm -rf "$SCRIPT_PATH"
else
	echo "[-] $SCRIPT_PATH doesn't exist"
fi

if [[ -f "$SERVICE_PATH/$SERVICE_FILE" ]]; then
	echo "[+] Removing $SERVICE_PATH/$SERVICE_FILE"
	rm "$SERVICE_PATH/$SERVICE_FILE"
else
	echo "[-] $SERVICE_PATH/$SERVICE_FILE doesn't exist"
fi

systemctl daemon-reload
systemctl daemon-reexec
