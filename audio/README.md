# Audio Lulz

I can see you but can't hear you... can you hear me now?

* The SIM7600G-H Hat is capable of dialing and answering calls
	* Could Audio over the cellular network compliment, or be used as a fallback when media streaming fails?
	* Are there any potential benefits to being able to use the voice call feature?
* The SIM7600G-H has one jack for earpiece output and mic input
* [Sabrent USB External Stereo Sound Adapter](https://www.amazon.com/Sabrent-External-Adapter-Windows-AU-MMSA/dp/B00IRVQ0F8) has audio out (stereo) and mic (mono) in.

* Speech to Text
	* [DeepSpeech on the Jetson Nano](http://williamsportwebdeveloper.com/cgi/wp/?p=3568)
* Text > GPT3 > Response
* Response to Speech

## Speech to Text

### DeepSpeech for Jetson Nano (0.6.0)

* [guide](http://williamsportwebdeveloper.com/cgi/wp/?p=3568)
* [releases](https://github.com/domcross/DeepSpeech-for-Jetson-Nano/releases)

## Text to Speech

* [ISAAC](https://docs.nvidia.com/isaac/isaac/packages/audio/doc/text_to_speech.html)
* Builtin Linux Tools: `spd-say, say, etc...`

### Hardware

1. Plug in the Sabrent USB External Stereo Sound Adapter.
1. Connect a 1/8" to 1/8" aux cable in the green, headphone output jack.
1. Connect the other end to the audio jack on the SIM7600G-H

### Software  

1. `spd-say` is a basic text to speech tool included in Ubuntu 18.04 distributions`
1. Install say: `sudo apt-get install gnustep-gui-runtime`
1. Create your message. Make sure to close it with a newline (enter/return).

### Dialing with the SIM7600GH

You'll need two terminal windows.

1. In the first, run `$ sudo cat /dev/ttyUSB2`. In the second run the rest of the commands
1. `$ sudo /bin/bash -c "echo -e \"ATD<phone_number>;\r\" > /dev/ttyUSB2"`
1. In the first window, you should see some activity. When you see `VOICE CALL: BEGIN` that means the call has begun; someone picked up on the other end.
1. spd-say is included in Ubuntu 18.04: `while read line; do spd-say -w "$line";done < sample.txt`
1. say gives you slightly more control over the voice characteristics: `while read line; do say "$line";done < sample.txt`
1. `$ sudo /bin/bash -c "echo -e \"AT+CHUP\r\" > /dev/ttyUSB2"` ends the call.

* All of this is scripted in `prank.sh`

## Quirks

The cheapo USB Audio dongle at times needed to be reset. Not sure if this is because of power saving settings. I [found a way](https://askubuntu.com/questions/645/how-do-you-reset-a-usb-device-from-the-command-line) to reset the device, which seemed to bring it back online. A bit kludgy and hopefully something that a future higher quality device won't require. Another possible soultion is [here](http://billauer.co.il/blog/2013/02/usb-reset-ehci-uhci-linux/).