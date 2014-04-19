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
		self.subs = {}
		self.collections = {}
		self.pending_msg = []
		self.dispatcher = {"added": self.on_added, "error": self.on_error, 
							"result": self.on_result, "changed": self.on_changed,
							"ready": self.on_ready}

	def send(self, msg_dict):
		message = json.dumps(msg_dict)
		super(DDPClient, self).send(message)

	#called after handshake confirmed
	def opened(self):
		self.send({"msg": "connect", "version": self.DDP_VER[0], "support": self.DDP_VER})

	#called if the websocket is closed
	def closed(self, code, reason=None):
		print "Shut down", code, reason

	#called when received a message from the server
	def received_message(self, m):
		msg = json.loads(str(m))
		if 'msg' in msg:
			m_txt = msg['msg']
			if m_txt in self.dispatcher:
				self.dispatcher[m_txt](msg)

			elif m_txt == "connected":
				self.connected = True
				print "connected"
	

	#called when the subscribition has been enabled
	def on_ready(self, msg):
		for i in msg['subs']:
			self.subs[i]['ready'] = True

	#called when a result message is recieved
	def on_result(self, msg):
		if msg['id'] in self.pending_msg:
			indx = self.pending_msg.index(msg['id'])
			print "message recieved"
			del self.pending_msg[indx]

	#called on an error message	
	def on_error(self, msg):
		print msg

	#called when a document has been changed
	def on_changed(self, msg):
		indx = 0
		coll = self.collections[msg['collection']]
		for item in coll:
			if item['id'] == msg['id']:
				break
			indx += 1

		coll[indx] = msg['fields']
		coll[indx]['id'] = msg['id']
		#self.collections[msg['collection']] = coll


	#called when a document is added to the collection			
	def on_added(self, msg):
		if not msg['collection'] in self.collections:
			self.collections[msg['collection']] = []
		fields = msg['fields']
		fields['id'] = msg['id']
		self.collections[msg['collection']].append(fields)

	#used to subscribe to a meteor collection
	def subscribe(self, sub_name, params=None):
		msg = {"msg" : "sub"}
		msg['id'] = str(uuid.uuid4())
		msg['name'] = sub_name
		if(params != None):
			msg['params'] = params

		to_append = msg
		to_append['ready'] = False
		self.subs[msg['id']] = to_append  
		self.send(msg)

	#used to call a method
	def call(self, method, params):
		msg = {"msg" : "method"}
		msg['method'] = method
		msg['params'] = params
		msg['id'] = str(uuid.uuid4())


		self.pending_msg.append(msg['id'])
		self.send(msg)

	def login(self, username, password):
		self.call("login", [{"password": password, "user": {"username": username}}])


if __name__ == '__main__':
	try:
		ws = DDPClient("localhost", 3000)
		ws.connect()
		count = 1
		new_msg = False
		msg_count = 0
		epoch = 0
		while True:
			epoch += 1
			
			if msg_count > len(ws.pending_msg):
				new_msg = False

			msg_count = len(ws.pending_msg)
			if ws.connected and count == 1:
				ws.login("sam", "johnson")
				ws.subscribe("spending")
				count -= 1

	except KeyboardInterrupt:
		print ws.collections
		ws.close()