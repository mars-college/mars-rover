#! /usr/bin/python3

import os.path
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

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
     self.render("index.html")

	
class WSHandler(tornado.websocket.WebSocketHandler):
  def open(self):
    print ('[WS] Connection was opened.')
 
  def on_message(self, message):
    print ('[WS] Incoming message:', message)
    pass

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

#End of Program
