import RPi.GPIO as GPIO
from time import sleep

LED_PIN = 12

led_state = False
count = 0


GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW) # make pin into an output


while count < 1000:
	sleep(.01)
	if count % 2 == 0:
		led_state = not led_state
	GPIO.output(LED_PIN,led_state)
	count+=1

GPIO.cleanup()

exit()