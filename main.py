import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from ddpclient import DDPClient

class BackendManager():

	subs = ['userData', 'budget', 'spending', 'savingsGoals']

	def __init__(self):
		self.ddp = DDPClient(self, "localhost", 3000)
		self.ddp.connect()
		self.login = LoginScreen()
		self.login.set_manager(self)
		self.subs_ready = 0
		self.dispatcher = {"login": self.notify_login}

	def notify(self, method):
		if method in self.dispatcher:
			self.dispatcher[method]()

	def notify_login(self):
		#change screen to app, etc.
		print "logged in"
		self.setup_subs()
	
	def notify_ready(self):
		self.subs_ready += 1
		if self.subs_ready == len(self.subs): #all substriptions have been enabled
			total = 0
			for exp in self.ddp.collections['expenses'][0]['spending']:
				total += float(exp['amount'])

			total = float(self.ddp.collections['budgets'][0]['total']) - total

			self.login.total.text += str(total)


	def login_user(self, u, pwd):
		#change screen to loading
		self.ddp.login(u, pwd)

	def setup_subs(self):
		if(self.ddp.logged_in):
			for sub in self.subs:
				self.ddp.subscribe(sub)


class LoginScreen(Widget):
	f_username = ObjectProperty(None)
	f_password = ObjectProperty(None)
	total = ObjectProperty(None)

	manager = None

	def set_manager(self, manager):
		self.manager = manager	

	def login(self):
		uname = self.f_username.text
		pwd = self.f_password.text
		self.manager.login_user(uname, pwd)

class MoneybagsApp(App):
	def on_start(self):
		pass

	def on_stop(self):
		pass

	def on_pause(self):
		pass

	def build(self):
		manager = BackendManager()
		return manager.login

if __name__ == '__main__':
	MoneybagsApp().run()