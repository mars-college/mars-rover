#!/bin/bash

NUMBER="7202174677"
MESSAGE_FILE="sample.txt"
DEV="/dev/ttyUSB2"

function usage {
	echo -e "\nUsage: ./prank.sh [-d [device]] [-n [number]] [-f [message]]"
	echo -e "NOTE: Some network changes require your password"
	echo -e "\t-d\t\tspecify mobile device (default: /dev/ttyUSB2)"
	echo -e "\t-n\t\tspecify a 10-digit phone number (default: 7202174677)"
	echo -e "\t-f\t\tspecify a .txt file to read (default: sample.txt)"
	echo -e "\t-h\t\tdisplay this help message"
	echo -e "\n"
}

while getopts "d:f:n:h" opt; do
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
	spd-say -w -t female3 -o espeak-ng "$line"
done < "$MESSAGE_FILE"

echo "[*] Ending call"
sudo /bin/bash -c "echo -e \"AT+CHUP\r\" > $DEV"

exit 0

