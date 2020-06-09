import sys
import argparse
from signal import *
import time
import Jetson.GPIO as GPIO

def shutdown(sig):
	try:
		GPIO.cleanup()
	except:
		print("Shutdown of Jetson.GPIO failed.")
		pass
	sys.exit(0)

#------------------------------------------------------------------------
#	Signal Interrupt/Terminate Handlers

# catch control+c
def SIGINT_handler(sig, frame):
	shutdown(sig)

# catch termination signals from the system
def SIGTERM_handler(sig, frame):
	shutdown(sig)
#------------------------------------------------------------------------
# main

def main():

	# if os.getuid() != 0:
	# 	print("Must be run as root.")
	# 	sys.exit(1)

	# interrupt and terminate signal handling
	signal(SIGINT, SIGINT_handler)
	signal(SIGTERM, SIGTERM_handler)

	#-------------------------------------------------------------------
	# argument stuff
	ap = argparse.ArgumentParser()
	#ap.add_argument("-l","--lhost", default="", required=False, help="LHOST IP")
	#ap.add_argument("-p","--lport", type=int, default=31337, required=False, help="LHOST PORT")
	#ap.add_argument("-c", "--chunk-size", type=int, default=1024, required=False, help="chunk size in bytes")
	#ap.add_argument("-r", "--frame-rate", type=float, default=30, required=False, help="frames per second")
	#ap.add_argument("-s", "--frame-size", type=int, default=4, required=False, help="number of bytes to display per frame")
	#ap.add_argument("-b", "--frame-buffer", type=int, default=4, required=False, help="number of bytes stored prior to updating")
	#ap.add_argument('-v', "--verbose", action='store_true', default=False, help='Verbose mode. Display debug messages')
	args = ap.parse_args()

	# HOST = args.lhost
	# PORT = args.lport
	# CHUNK = args.chunk_size
	# RATE = args.frame_rate
	# FRAME_SIZE = args.frame_size
	# BUFFER_SIZE = args.frame_buffer 
	# VERBOSE = args.verbose

	#------------------------------------------------------------------------
	#	verbose or debug mode

	def debug(message):
		if VERBOSE:
			print(message)

	if VERBOSE:
		debug("Verbose mode. Displaying debug messeges")

	print("doing nothing. exiting.")
	GPIO.cleanup()

	# while True:
	# 	pass

if __name__ == '__main__':
	main()