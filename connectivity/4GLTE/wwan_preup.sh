#!/bin/bash

MODULE="simcom_wwan"
IFACE="wwan0"
DEV="ttyUSB2"

function usage {
	echo -e "\nUsage: wann_preup [-d [device]] [-i [interface]]"
	echo -e "NOTE: Some network changes require your password"
	echo -e "\t-d\t\tspecify device (default: /dev/ttyUSB2)"
	echo -e "\t-i\t\tspecify interface (default: wwan0)"
	echo -e "\t-h\t\tdisplay this help message"
	echo -e "\n"
}

while getopts "d:i:h" opt; do
	case ${opt} in
		h)
			usage
			exit 1
			;;
		i)
			IFACE=${OPTARG}
			;;
		d)
			DEV=${OPTARG}
			;;
		:)
			echo "[!] Option requires an argument."
			exit 1
			;;
		\?)
			echo "[!] Invalid option. Run with -h to view usage."
			exit 1
			;;
	esac
done
shift $((OPTIND -1))

if [ "$EUID" -ne 0 ]
  then echo "[!] Please run as root"
  exit 1
fi

if (lsmod | grep "$MODULE" >/dev/null 2>&1); then
	if (ifconfig -a | grep "$IFACE" >/dev/null 2>&1); then
<<<<<<< Updated upstream
		ifconfig "$IFACE" up
		if (ls /dev | grep "$DEV" >/dev/null 2>&1); then
			if (echo 'AT+CNMP=2' > "/dev/$DEV"); then
				if (echo 'AT$QCRMCALL=1,1' > "/dev/$DEV"); then
					echo "[+] $IFACE at /dev/$DEV is ready for IP Address"
					exit 0
=======

		echo 200 > /sys/class/gpio/export
		echo "out" > /sys/class/gpio/gpio200/direction
		echo 0 > /sys/class/gpio/gpio200/value
		sleep 1
		echo 1 > /sys/class/gpio/gpio200/value
		sleep 5
		echo 0 > /sys/class/gpio/gpio200/value
		sleep 20

		if (ifconfig "$IFACE" up >/dev/null 2>&1); then
			if (ls /dev | grep "$DEV" >/dev/null 2>&1); then
				if (echo 'AT+CNMP=38' > /dev/$DEV); then
					sleep 25
					if (echo 'AT$QCRMCALL=1,1' > /dev/$DEV); then
						sleep 5
						echo "[+] $IFACE at /dev/$DEV is ready for an IP Address"
						exit 0
					else
						echo "[!] Failed to activate 4G connection on $DEV"
						exit 1
					fi
>>>>>>> Stashed changes
				else
					echo "[!] unable to communicate with $DEV"
					ifconfig "$IFACE" down
					exit 1
				fi
			else
				echo "[!] /dev/$DEV not found"
				ifconfig "$IFACE" down
				exit 1
			fi
		else
			echo "[!] Could not bring up $IFACE."
			exit 1
		fi
	else
		echo "[!] interface $IFACE not found"
		exit 1
	fi
else
	echo "[!] $MODULE module not found"
	exit 1
fi