# Audio

I can see you but can't hear you... can you hear me now?

* The SIM7600G-H Hat is capable of dialing and answering calls
	* Could Audio over the cellular network compliment or be used as a fall back when media streaming fails?
	* Are there any potential benefits to being able to use the voice call feature?
* The SIM7600G-H has one jack for earpiece output and mic input
* [Sabrent USB External Stereo Sound Adapter](https://www.amazon.com/Sabrent-External-Adapter-Windows-AU-MMSA/dp/B00IRVQ0F8) has audio out (stereo) and mic (mono) in.

## Text to Speech

* Autodial / Answer and use GP2 generated text to "converse" with the person on the other end.
	1. SIM7600 audio out > Nano mic in
	1. speech to text?
	1. GP2 generated response > textfile.txt
	1. `spd-say < textfile.txt`
	1. audio out from Nano > SIM7600 mic in 

## Hardware

1. Plug in the Sabrent USB External Stereo Sound Adapter.
1. Connect a 1/8" to 1/8" aux cable in the green, headphone output jack.
1. Connect the other end to the audio jack on the SIM7600G-H

## Software  

1. Install say: `sudo apt-get install gnustep-gui-runtime`
1. Create your message. Make sure to close it with a newline (enter/return).

## Dialing with the SIM7600GH

You'll need two terminal windows.

1. In the first, run `$ sudo cat /dev/ttyUSB2`. In the second run the rest of the commands
1. `$ sudo su`
1. `# echo -e 'ATD<phone_number>;\r' > /dev/ttyUSB2`
1. In the first window, you should see some activity. When you wee `VOICE CALL: BEGIN` that means dialing has begun.
1. spd-say is included: `while read line; do spd-say -w "$line";done < sample.txt`
1. say gives you slightly more control over the voice characteristics: `while read line; do say "$line";done < sample.txt`
1. `# echo -e 'AT+CHUP\r' > /dev/ttyUSB2` ends the call.

## LOL!!!