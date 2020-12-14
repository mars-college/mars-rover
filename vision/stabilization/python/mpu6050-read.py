#!/usr/bin/python3

from mpu6050 import mpu6050
from time import time, sleep

I2C_ADDRESS=0x68

'''
ACCEL_SCALE_MODIFIER_2G = 16384.0
ACCEL_SCALE_MODIFIER_4G = 8192.0
ACCEL_SCALE_MODIFIER_8G = 4096.0
ACCEL_SCALE_MODIFIER_16G = 2048.0

GYRO_SCALE_MODIFIER_250DEG = 131.0
GYRO_SCALE_MODIFIER_500DEG = 65.5
GYRO_SCALE_MODIFIER_1000DEG = 32.8
GYRO_SCALE_MODIFIER_2000DEG = 16.4

ACCEL_RANGE_2G = 0x00
ACCEL_RANGE_4G = 0x08
ACCEL_RANGE_8G = 0x10
ACCEL_RANGE_16G = 0x18

GYRO_RANGE_250DEG = 0x00
GYRO_RANGE_500DEG = 0x08
GYRO_RANGE_1000DEG = 0x10
GYRO_RANGE_2000DEG = 0x18
'''

FIFO_EN = 0x23
FIFO_CONF = 0b01110000 # just interersted in the gyros for now
FIFO_COUNT = 0x72
FIFO_DATA = 0x74
FIFO_PACKET_SIZE = 6 # two bytes for each: GX, GY, GZ
FIFO_BYTES_TO_READ = 600

#Interrupt Registers
INT_ENABLE = 0x38 #
INT_STATUS = 0x3A
INT_CONF = 0b00010001
INT_PIN_CFG = 0x37
INT_PIN_CFG_CONF = 0b00010000

#Sample Rate Dividr
SMPRT_DIV = 0x19
SMPRT_DIV_CONF = 0x00 

# Config

CONFIG = 0x1A
CONFIG_CONF = 0x4 # DLPF @ 20Hz

#User Control
USER_CTL = 0x6A
USER_CTL_CONF = 0b01000000 # enable FIFO
USER_CTL_FIFO_RESET = 0b00000100 # disable and reset FIFO

PWR_MGMT_1 = 0x6B
PWR_MGMT_1_RST = 1 << 7
PWR_MGMT_1_CONF = 3



ACCEL_RANGE = mpu6050.ACCEL_RANGE_4G
GYRO_RANGE = mpu6050.GYRO_RANGE_2000DEG


IMU = mpu6050(I2C_ADDRESS)

verbose = True

def debug(message, result=2):

	if verbose:
		status=""
		if result == 0:
			status = "[+] " # success
		elif result == 2:
			status = "[*] " # task
		elif result == 1:
			status = "[!] " # error
		else:
			status = "[?] " # unrecognized result
		print(status + message)

def read_FIFO_word(dev, register=FIFO_DATA):
        # Read the data from the FIFO register
        high = dev.bus.read_byte_data(dev.address, register)
        low = dev.bus.read_byte_data(dev.address, register)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

def read_FIFO(offsets={'x':0.0,'y':0.0,'z':0.0}):

	# interested in only the gyro data for now
	# each packet is one gyro sample

	packet_count = 0
	byte_count = IMU.read_i2c_word(FIFO_COUNT)
	
	while byte_count < FIFO_BYTES_TO_READ:
		byte_count = IMU.read_i2c_word(FIFO_COUNT)

	packets = []

	while packet_count < int(FIFO_BYTES_TO_READ/FIFO_PACKET_SIZE): 
		x = read_FIFO_word(IMU)/IMU.GYRO_SCALE_MODIFIER_2000DEG - offsets['x']
		y = read_FIFO_word(IMU)/IMU.GYRO_SCALE_MODIFIER_2000DEG - offsets['y']
		z = read_FIFO_word(IMU)/IMU.GYRO_SCALE_MODIFIER_2000DEG - offsets['z']
		packets.append( {'x':x,'y':y,'z':z}  )	
		packet_count+=1
	
	reset_FIFO()

	return packets

def reset_FIFO():
	#Disable FIFO and issue RESET
	IMU.bus.write_byte_data(IMU.address, USER_CTL, USER_CTL_FIFO_RESET)
	#Enable FIFO
	IMU.bus.write_byte_data(IMU.address, USER_CTL, USER_CTL_CONF)

def setup():

	# Reset the MPU6050
	debug("Reseting and using Z-axis gyro as clock source ", 2)
	IMU.bus.write_byte_data(IMU.address, PWR_MGMT_1, PWR_MGMT_1_RST)
	sleep(5)
	IMU.bus.write_byte_data(IMU.address, PWR_MGMT_1, PWR_MGMT_1_CONF)
	check = IMU.bus.read_byte_data(IMU.address, PWR_MGMT_1)
	debug("Check value = "+format(check,'08b'), 2)
	if check == PWR_MGMT_1_CONF:
		debug("Clock source set.")
	elif check == -1:
		debug("Something went wrong...", 1)
	else:
		debug("Failed to set clock source", 1)

	# Set the samplerate
	debug("Setting sample rate to range to " + str(SMPRT_DIV_CONF), 2)
	IMU.bus.write_byte_data(IMU.address, SMPRT_DIV, SMPRT_DIV_CONF)
	check = IMU.bus.read_byte_data(IMU.address, SMPRT_DIV)
	debug("Check value = "+str(check), 2)
	if check == SMPRT_DIV_CONF:
		debug("Sample range set.")
	elif check == -1:
		debug("Something went wrong...", 1)
	else:
		debug("Failed to set sample rate", 1)

	# Configure LPF and FSYNC
	debug("Configuring LPF and FSYNC", 2)
	IMU.bus.write_byte_data(IMU.address, CONFIG, CONFIG_CONF)
	check = IMU.bus.read_byte_data(IMU.address, CONFIG)
	debug("Check value = "+str(check), 2)
	if check == CONFIG_CONF:
		debug("Configuration successful")
	elif check == -1:
		debug("Something went wrong...", 1)
	else:
		debug("Failed to set configuration", 1)
	
	# Set the accelerometer range
	debug("Setting accelerometer range to " + str(ACCEL_RANGE), 2)
	IMU.set_accel_range(ACCEL_RANGE)
	check = IMU.read_accel_range(True)
	debug("Check value = "+str(check), 2)
	if check == ACCEL_RANGE:
		debug("Accelerometer range set to "+str(ACCEL_RANGE), 0)
	elif check == -1:
		debug("Something went wrong...", 1)
	else:
		debug("Failed to set accelerometer range to " + str(ACCEL_RANGE), 1)
	debug("Current accelerometer range is " + str(check), 0)

	# Set the gyroscope range
	debug("Setting gyroscope range to " + str(GYRO_RANGE), 2)
	IMU.set_gyro_range(GYRO_RANGE)
	check = IMU.read_gyro_range(True)
	debug("Check value = "+str(check), 2)
	if check == GYRO_RANGE:
		debug("Gyroscope range set to "+str(GYRO_RANGE), 0)
	elif check == -1:
		debug("Something went wrong...", 1)
	else:
		debug("Failed to set gyroscope range to " + str(GYRO_RANGE), 1)
	debug("Current gyroscope range is " + str(check), 0)
	
	# Setup FIFO_EN
	debug("Configuring FIFO_EN register", 2)
	IMU.bus.write_byte_data(IMU.address, FIFO_EN, FIFO_CONF)
	check = IMU.bus.read_byte_data(IMU.address, FIFO_EN)
	debug("Check value = "+ format(check, '08b'), 2)
	if check == FIFO_CONF:
		debug("FIFO_EN successfully configured", 0)
	else:
		debug("Failed to configure FIFO_EN. Expected: " + str(FIFO_CONF) + ". Got: " + str(check) , 1)

	# Setup INT_ENABLE
	debug("Configuring INT_ENABLE register", 2)
	IMU.bus.write_byte_data(IMU.address, INT_ENABLE, INT_CONF)
	check = IMU.bus.read_byte_data(IMU.address, INT_ENABLE)
	debug("Check value = "+format(check, '08b'), 2)
	if check == INT_CONF:
		debug("INT_ENABLE successfully configured", 0)
	else:
		debug("Failed to configure INT_ENABLE. Expected: " + str(FIFO_CONF) + ". Got: " + str(check) , 1)

def get_average_offsets():

	offset = { 'x': 0.0, 'y': 0.0, 'z': 0.0 }

	count = 0
	samples = []

	while count < 5000:
		samples.append(IMU.get_gyro_data())
		count += 1

	for s in samples:
		offset['x']+=s['x']
		offset['y']+=s['y']
		offset['z']+=s['z']

	offset['x']/=count
	offset['y']/=count
	offset['z']/=count
	return offset


def main():
	
	rotation = { 'x': 0.0, 'y': 0.0, 'z': 0.0 }
	
	setup()

	offsets = get_average_offsets()
	print(offsets)
	
	count = 0

	reset_FIFO()

	while True:
		
		data = read_FIFO(offsets)

		for d in data:
		 	rotation['x'] += d['x'] / 1000
		 	rotation['y'] += d['y'] / 1000
		 	rotation['z'] += d['z'] / 1000
		
		print("Rotation: ", rotation)


if __name__ == "__main__":
	main()