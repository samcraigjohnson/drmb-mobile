from ws4py.client.threadedclient import WebSocketClient
import json
import uuid


class DDPClient(WebSocketClient):

	DDP_VER = ["pre1"]
	WS_URL = "ws://{}:{}/websocket"

	def __init__(self, server, port=80):
		url = self.WS_URL.format(server, str(port))
		WebSocketClient.__init__(self, url)
		self.connected = False
		self.subs = []


	def send(self, msg_dict):
		message = json.dumps(msg_dict)
		print "Sending message...", message
		super(DDPClient, self).send(message)

	#called after handshake confirmed
	def opened(self):
		self.send({"msg": "connect", "version": self.DDP_VER[0], "support": self.DDP_VER})
		print "attempting to handshake"

	def closed(self, code, reason=None):
		print "Shut down", code, reason

	def received_message(self, m):
		print m
		msg = json.loads(str(m))
		if(msg.get('msg') == "connected"):
			self.connected = True
			print msg

	def subscribe(self, sub_name, params=None):
		msg = {"msg" : "sub"}
		msg['id'] = "testSub"
		msg['name'] = sub_name
		if(params != None):
			msg['params'] = params

		self.send(msg)

	def call(self, method, params):
		msg = {"msg" : "method"}
		msg['method'] = method
		msg['params'] = params
		msg['id'] = "testCall"

		self.send(msg)

	def login(self, username, password):
		self.call("login", [{"password": password, "user": {"username": username}}])


if __name__ == '__main__':
	try:
		ws = DDPClient("localhost", 3000)
		ws.connect()
		count = 1
		while True:
			if ws.connected and count == 1:
				print "WORKS!"
				print "subscribing"
				ws.login("sam", "johnson")
				count -= 1

	except KeyboardInterrupt:
		ws.close()