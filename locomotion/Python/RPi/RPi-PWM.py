import pigpio
from time import sleep

M1_PIN = 12
M2_PIN = 13

count = 0
m1_rate = 333
m2_rate = 500
PWM_RANGE = 1024

print("[*] Activating PWM...")

pigpio.exceptions = True
PWM = pigpio.pi()
PWM_FREQ = 20000 # frequency of PWM

if not PWM.connected:
	print("[!] Failed to activate PWM...")
	exit()

print("[+] Successfully activated PWM.")

PWM.set_PWM_frequency(M1_PIN, PWM_FREQ)
PWM.set_PWM_frequency(M2_PIN, PWM_FREQ)
PWM.set_PWM_range(M1_PIN, PWM_RANGE)
PWM.set_PWM_range(M2_PIN, PWM_RANGE)

print("[*] Running for 10 seconds...")

while count < 1000:
	sleep(.01)
	PWM.set_PWM_dutycycle(M1_PIN, int((count%m1_rate)/m1_rate*PWM_RANGE))
	PWM.set_PWM_dutycycle(M2_PIN, int((count%m2_rate)/m2_rate*PWM_RANGE))
	count+=1

print("[*] Deactivating PWM.")

PWM.set_PWM_dutycycle(M1_PIN, 0)
PWM.set_PWM_dutycycle(M2_PIN, 0)
PWM.stop()

print("[+] Done!")

exit()