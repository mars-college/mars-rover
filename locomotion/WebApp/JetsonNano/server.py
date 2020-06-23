#! /usr/bin/python3

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from smbus import SMBus
from time import sleep
import math

left_direction = True
right_direction = True
left_direction_last = True
right_direction_last = True

ADDRESSES = [ 0x10 , 0x11 ]

bus = SMBus(1)

def send_i2c_data(address, data):
  try:
    bus.write_i2c_block_data( address, 0, data )
  except Exception as e:
      print(e)
      pass

def set_power(drive, turn):

  if drive > 0:
    left_power = drive + turn
    right_power = drive - turn
  else:
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
    send_i2c_data( ADDRESSES[0], [ ord('d'), int(left_direction) ] )


  if right_direction == right_direction_last:
    send_i2c_data( ADDRESSES[1], [ ord('d'), int(right_direction) ] )


  left_power = int(min(abs(left_power), 255))
  right_power = int(min(abs(right_power), 255))
  
  send_i2c_data(ADDRESSES[0], [ ord('p'), left_power ] )
  send_i2c_data(ADDRESSES[1], [ ord('p'), right_power ] )


  return left_direction, right_direction

settings = dict(
	template_path = os.path.join(os.path.dirname(__file__), "templates"),
	static_path = os.path.join(os.path.dirname(__file__), "static")
	)

#Tonado server port
PORT = 80


class MainHandler(tornado.web.RequestHandler):
  def get(self):
     print ("[HTTP](MainHandler) User Connected.")
     self.render("index.html")

	
class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print ('[WS] Connection was opened.')
 
  def on_message(self, message):

    global left_direction_last
    global right_direction_last

    drive = 0
    turn = 0

    # print ('[WS] Incoming message:', message)

    message = message.split(',')
    # print ('[WS] Incoming message:', message)

    if message[0] == 'j':
      drive = int(256 * float(message[1]))
      turn = int(256 * float(message[2]))
      # print("Drive: "+str(drive)+"Turn: "+str(turn))
      left_direction_last, right_direction_last = set_power( drive , turn )

    if message[0] == "on_g":
        send_i2c_data(ADDRESSES[0], [ ord('b'), 255 ] )
        send_i2c_data(ADDRESSES[1], [ ord('b'), 255 ] )
    if message[0] == "off_g":
        send_i2c_data(ADDRESSES[0], [ ord('b'), 0 ] )
        send_i2c_data(ADDRESSES[1], [ ord('b'), 0 ] )
      
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
        print ("")
        print ("Exception triggered - Tornado Server stopped.")

#End of Program
