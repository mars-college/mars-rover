import pigpio
from time import sleep
import math

def main():

	#BCM pin numbers
	APWM= 12
	AIN1 = 4
	AIN2 = 17
	BPWM = 13
	BIN1 = 27
	BIN2 = 22

	count = 0
	m1_rate = 250
	m2_rate = 333
	PWM_RANGE = 1024
	left_direction = True
	right_direction = True
	left_direction_last = True
	right_direction_last = True

	print("[*] Activating PWM...")

	pigpio.exceptions = True
	GPIO = pigpio.pi()
	PWM_FREQ = 1000 # frequency of PWM

	if not GPIO.connected:
		print("[!] Failed to activate PWM...")
		exit()

	print("[+] Successfully activated PWM.")

	GPIO.set_PWM_frequency(APWM, PWM_FREQ)
	GPIO.set_PWM_frequency(BPWM, PWM_FREQ)
	GPIO.set_PWM_range(APWM, PWM_RANGE)
	GPIO.set_PWM_range(BPWM, PWM_RANGE)

	GPIO.set_mode(AIN1, pigpio.OUTPUT)
	GPIO.set_mode(AIN2, pigpio.OUTPUT)
	GPIO.set_mode(BIN1, pigpio.OUTPUT)
	GPIO.set_mode(BIN2, pigpio.OUTPUT)

	def clearOutput():
		GPIO.write(AIN1, 0)
		GPIO.write(AIN2, 0)
		GPIO.write(BIN1, 0)
		GPIO.write(BIN2, 0)
		GPIO.set_PWM_dutycycle(APWM, 0)
		GPIO.set_PWM_dutycycle(BPWM, 0)

	def m1_direction(direction):
		
		if direction:
			GPIO.write(AIN1, 0)
			GPIO.write(AIN2, 1)
		else:
			GPIO.write(AIN1, 1)
			GPIO.write(AIN2, 0)

	def m2_direction(direction):
		
		if direction:
			GPIO.write(BIN1, 0)
			GPIO.write(BIN2, 1)
		else:
			GPIO.write(BIN1, 1)
			GPIO.write(BIN2, 0)

	def set_power(drive, turn):

		left_power = drive - turn
		right_power = drive + turn

		if left_power >= 0:
			left_direction = True
		else:
			left_direction = False

		if right_power >= 0:
			right_direction = True
		else:
			right_direction = False

		if left_direction == left_direction_last:
			m1_direction(left_direction)

		if right_direction == right_direction_last:
			m2_direction(right_direction)

		left_power = min(abs(left_power),PWM_RANGE)
		right_power = min(abs(right_power),PWM_RANGE)

		GPIO.set_PWM_dutycycle(APWM, left_power)
		GPIO.set_PWM_dutycycle(BPWM, right_power)

		return left_direction, right_direction

	clearOutput()

	print("[*] Running for 10 seconds...")

	while count < 1000:
		sleep(.01)
		drive = int(math.sin(2*math.pi*(count%m2_rate)/m2_rate)*PWM_RANGE) 
		turn = int(math.sin(2*math.pi*(count%m1_rate)/m1_rate) * PWM_RANGE)
		left_direction_last, right_direction_last = set_power( drive , turn)
		count+=1

	print("[*] Deactivating PWM.")

	clearOutput()
	GPIO.stop()

	print("[+] Done!")

	exit()

if __name__ == '__main__':
	main()