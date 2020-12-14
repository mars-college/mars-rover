import serial
import json
from time import sleep
from time import time

# mpu is the mpu9250 connected to an arduino nano
# right now it just spews data over serial
# would like to have it return one sample on request
# could look into faster methods, but for now this will do

DEV = '/dev/ttyUSB5'
BAUD = 115200
def main():

	imu = serial.Serial( DEV , BAUD )

	while True:
		start_time = time()
		
		# gets bytes from the serial buffer (blocking)
		data = imu.readline()

		# cleanup bytes and make it a pretty string
		try:
			data = data.decode().strip()
		except:
			pass

		# arduino formats roll pitch yaw to something like json
		if data[0] == '{' and data[-1] == '}' :

			try:
				data = json.loads(data)
			except:
				pass

			# show us what you got
			if data['status'] == 0:
				print("Starting up...")
			elif data['status'] == 1:
				print("Roll: ", data['roll'], ", Pitch: ", data['pitch'], ", Yaw: ", data['yaw'])
				sleep( 1.0 / 60.0 )
			else:
				print("Check yourself!")
				exit()

		
		# use this to fetch the state of the imu
		imu.write('fetch\n'.encode('utf-8'))

if __name__ == "__main__":
	main()