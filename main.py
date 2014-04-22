import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from ddpclient import DDPClient


class BackendManager():

	subs = ['userData', 'budget', 'spending', 'savingsGoals']

	def __init__(self):
		self.ddp = DDPClient(self, "localhost", 3000)
		self.ddp.connect()
		
		self.sm = ScreenManager(transition=NoTransition())
		self.login = LoginScreen(name="Login")
		self.login.set_ddp_manager(self)
		self.main_screen = MainScreen(name="Main")
		self.main_screen.set_ddp_manager(self)

		self.sm.add_widget(self.login)
		self.sm.add_widget(self.main_screen)

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

			budj = self.ddp.collections['budgets'][0]
			total = float(budj['total']) - total - float(budj['save'])

			self.main_screen.total.text += str(total)
			self.sm.current = "Main"


	def login_user(self, u, pwd):
		#change screen to loading
		self.ddp.login(u, pwd)

	def setup_subs(self):
		if(self.ddp.logged_in):
			for sub in self.subs:
				self.ddp.subscribe(sub)


class LoginScreen(Screen):
	f_username = ObjectProperty(None)
	f_password = ObjectProperty(None)
	ddp_manager = None

	def set_ddp_manager(self, ddp_manager):
		self.ddp_manager = ddp_manager	

	def login(self):
		uname = self.f_username.text
		pwd = self.f_password.text
		self.ddp_manager.login_user(uname, pwd)

class MainScreen(Screen):
	total = ObjectProperty(None)
	ddp_manager = None

	def set_ddp_manager(self, ddp_manager):
		self.ddp_manager = ddp_manager	

class MoneybagsApp(App):
	def on_start(self):
		pass

	def on_stop(self):
		pass

	def on_pause(self):
		pass

	def build(self):
		ddp_manager = BackendManager()
		return ddp_manager.sm

if __name__ == '__main__':
	MoneybagsApp().run()