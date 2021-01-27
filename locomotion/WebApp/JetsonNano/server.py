#! /usr/bin/python3

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from smbus import SMBus
from time import sleep
import math

# Tornado resource paths
settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)

# Tonado server port
PORT = 80

# i2c variables
bus = SMBus(1)
ADDRESSES = [ 0x10 , 0x11 ]

# contrl variables
left_direction_last = True
right_direction_last = True
left_power_last = 0
right_power_last = 0


def init_motors():
    # set direction to forward
    send_i2c_data( ADDRESSES[0], [ ord('d'), int(True) ] )
    send_i2c_data( ADDRESSES[1], [ ord('d'), int(True) ] )
    # set power to 0
    send_i2c_data( ADDRESSES[0], [ ord('p'), 0 ] )
    send_i2c_data( ADDRESSES[1], [ ord('p'), 0 ] )

def set_power(drive, turn):
  # NOTE: this is currently designed around a single joystick UI.
  # May need to be tweaked for dual joystick gamepad controllers

  # contrain and scale values to 
  drive = constrain( drive, -1.0 ,1.0) * 256
  turn = constrain( turn, -1.0 ,1.0) * 256

  # cacluate power
  if drive <= 0: # forward
    left_power = drive + turn
    right_power = drive - turn
  else: # reverse
    left_power = drive - turn
    right_power = drive + turn

  # set direction based on power
  if left_power >= 0:
    left_direction = True
  else:
    left_direction = False

  if right_power >= 0:
    right_direction = True
  else:
    right_direction = False

  # NOTE: commented out code to send direction changes only for I2C spam suppression
  # not sure if this is entirely necessary
  
  #if left_direction != left_direction_last:
  send_i2c_data( ADDRESSES[0], [ ord('d'), int(left_direction) ] )

  #if right_direction != right_direction_last:
  send_i2c_data( ADDRESSES[1], [ ord('d'), int(right_direction) ] )

  # absolute value constrained to integer values 0-255
  left_power = int(min(abs(left_power), 255))
  right_power = int(min(abs(right_power), 255))
  
  #if left_power != left_power_last:
  send_i2c_data(ADDRESSES[0], [ ord('p'), left_power ] )
  #if right_power != right_power_last:
  send_i2c_data(ADDRESSES[1], [ ord('p'), right_power ] )

  return left_direction, right_direction, left_power, right_power

def constrain( _val, _min, _max):
  return min(_max, max(_min,_val))

# Note to future self: Make the Atmega code for the motor control more robust...
# 1. Make the communication bi-directional, indicating whether speed was received and applied correctly
# 2. By default, the motor speed should be set to 0 unless the speed was successfully applied
# 3. If necessary, develop an error code so this server knows what to do when things go wrong in different ways

def send_i2c_data(address, data):
  try:
    bus.write_i2c_block_data( address, 0, data )
  except Exception as e:
    print(e)
    pass

class MainHandler(tornado.web.RequestHandler):
  def get(self):
     print ("[HTTP](MainHandler) User Connected.")
     self.render("index.html")

class WSHandler(tornado.websocket.WebSocketHandler): 

  def open(self):
    print ('[WS] Connection was opened.')

  def on_close(self):
    # stop motors
    set_power( 0.0 , 0.0 )
    print ('[WS] Connection was closed.')

  def on_message(self, message):

    global left_direction_last
    global right_direction_last 
    global left_power_last
    global right_power_last

    message = message.split(',')
    # print ('[WS] Incoming message:', message)

    if message[0] == 'j':
      drive = float(message[1])
      turn = float(message[2])
      #left_direction_last, right_direction_last, left_power_last, right_power_last = set_power( drive , turn )
      set_power( drive , turn )

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
    except Exception as e:
        # Just incase the motors didn't get the message to stop...
        set_power( 0.0, 0.0 )
        # Ooops message
        print ("")
        print ("Exception triggered - Tornado Server stopped.")
        print ("---------------------------------------------")
        print (e)
        print ("---------------------------------------------")
        print ("Have a nice day! :)")


#End of Program
