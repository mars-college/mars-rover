#!/usr/bin/python3

from smbus2 import SMBus, i2c_msg
import time
import random

def main():


	bus = SMBus(1)
	
	address = [ 0x10, 0x11 ]

	while True:
		for i in range(len(address)):
			message = 'j,'+str(round(random.uniform(-1,1),4))+','+str(round(random.uniform(-1,1),4))
			print("[+]", message)
			message = list(message.encode('utf-8'))
			print("[+]",message)
			write = i2c_msg.write(address[i], message)
			read = i2c_msg.read(address[i], 16)
			print("[*] Issuing read/write")
			test = bus.i2c_rdwr(write, read)
		time.sleep(0.125)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print("---")
		print("[!] Exception triggered. Exiting")
		print(e)
		print("---")
