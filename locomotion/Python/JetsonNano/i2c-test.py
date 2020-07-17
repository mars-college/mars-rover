#!/usr/bin/python3

import smbus
import time

def main():

	count = 0

	bus = smbus.SMBus(0)
	address = 0x40

	while True:
		bus.write_byte_data(address, 0, count)
		count+=1
		count%=256
		print(count)
		time.sleep(0.125)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print ("")
		print ("Exception triggered. Exiting")
		print(e)
