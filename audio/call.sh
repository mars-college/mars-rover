#!/bin/bash

NUMBER=""
MESSAGE_FILE="sample.txt"
DEV="/dev/ttyUSB2"
VOICE=male1

function usage {
	echo -e "\nUsage: ./call.sh [-d [device]] [-n [number]] [-f [message]]"
	echo -e "NOTE: Some network changes require your password"
	echo -e "\t-d\t\tspecify mobile device (default: /dev/ttyUSB2)"
	echo -e "\t-n\t\tspecify a 10-digit phone number (default: 7202174677)"
	echo -e "\t-f\t\tspecify a .txt file to read (default: sample.txt)"
	echo -e "\t-v\t\tspecify voice (default: male1)"
	echo -e "\t-h\t\tdisplay this help message"
	echo -e "\n"
}

while getopts "d:f:n:v:h" opt; do
	case ${opt} in
		h)
			usage
			exit 1
			;;
		n)
			NUMBER="${OPTARG}"
			;;
		d)
			DEV="${OPTARG}"
			;;
		f)
			MESSAGE_FILE="${OPTARG}"
			;;
		v)
			VOICE="${OPTARG}"
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

echo "[*] Dialing $NUMBER"
sudo /bin/bash -c "echo -e \"ATD$NUMBER;\r\" > $DEV"

while read response; do
	echo "[*] $response"
	if [[ "$response" =~ "ERROR" ]];then
		echo "[!] Unable to dial out"
		exit 1
	elif [[ "$response" =~ "VOICE CALL: BEGIN" ]];then
		echo "[+] Call Succeeded"
		break
	elif [[ "$response" =~ "VOICE CALL: END" ]];then
		echo "[-] Receiver hung up"
		exit 0
	fi
done < <(sudo cat "$DEV")

while read line; do
	spd-say -w -o espeak-ng -P important -r -25 -t "$VOICE" "$line"
done < "$MESSAGE_FILE"

echo "[*] Ending call"
sudo /bin/bash -c "echo -e \"AT+CHUP\r\" > $DEV"

exit 0

