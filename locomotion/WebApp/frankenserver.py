#! /usr/bin/python3

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

#-----
import pigpio
from time import sleep
import math
#-----

APWM= 12
AIN1 = 4
AIN2 = 17
BPWM = 13
BIN1 = 27
BIN2 = 22

PWM_RANGE = 1024
left_direction = True
right_direction = True
left_direction_last = True
right_direction_last = True

print("[*] Activating pigpio GPIO...")

pigpio.exceptions = True
GPIO = pigpio.pi()
PWM_FREQ = 1000 # frequency of PWM

if not GPIO.connected:
  print("[!] Failed to activate GPIO...exiting!")
  exit()

print("[+] Successfully activated GPIO.")
print("[*] Setting up pins.")

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

clearOutput()

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

#import RPi.GPIO as GPIO

#Initialize Raspberry PI GPIO
#GPIO.setmode(GPIO.BOARD)

#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(13, GPIO.OUT)
#GPIO.setup(16, GPIO.OUT)
#GPIO.setup(18, GPIO.OUT)

#Tornado Folder Paths
settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)

#Tonado server port
PORT = 80


class MainHandler(tornado.web.RequestHandler):
  def get(self):
     print ("[HTTP](MainHandler) User Connected.")
     self.render("index2.html")

	
class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print ('[WS] Connection was opened.')
 
  def on_message(self, message):
    print ('[WS] Incoming message:', message)

    #-----
    message = message.split(';')

    drive = 0.0
    turn = 0.0

    if message[0] == 'd':
      drive == int(PWM_RANGE * float([1]))

    if message[0] == 't':
      turn == int(PWM_RANGE * float([1]))

    left_direction_last, right_direction_last = set_power( drive , turn)

    # if message == "on_g":
    #   GPIO.output(16, True)
    # if message == "off_g":
    #   GPIO.output(16, False)
      
    # if message == "on_r":
    #   GPIO.output(18, True)
    # if message == "off_r":
    #   GPIO.output(18, False)
      
    # if message == 'on_b':
    #   GPIO.output(11 , True)
    # if message == 'off_b':
    #   GPIO.output(11 , False)
      
    # if message == 'on_w':
    #   GPIO.output(13 , True)
    # if message == 'off_w':
    #   GPIO.output(13 , False)

  def on_close(self):
    print ('[WS] Connection was closed.')


application = tornado.web.Application([
  (r'/', MainHandler),
  (r'/ws', WSHandler),
  ], **settings)


if __name__ == "__main__":
    try:
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(PORT)
        main_loop = tornado.ioloop.IOLoop.instance()

        print ("Tornado Server started")
        main_loop.start()

    except:
        print ("Exception triggered - Tornado Server stopped.")
        clearOutput()
        GPIO.stop()

#End of Program
