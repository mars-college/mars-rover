import serial
import json
from time import sleep

# mpu is the mpu9250 connected to an arduino nano
# right now it just spews data over serial
# would like to have it return one sample on request
# could look into faster methods, but for now this will do

mpu = serial.Serial( '/dev/ttyUSB5' , 115200 )

# wait a little bit for folks to connect
sleep(5)

while True:
	# 
	mpu.write('fetch\n'.encode('utf-8'))

	# gets bytes from the serial buffer
	data = mpu.readline()

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
		else:
			print("Check yourself!")