import kivy
kivy.require('1.8.0')

from kivy.config import Config
Config.set("graphics", "width", 480)
Config.set("graphics", "height", 800)
Config.write()

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.storage.jsonstore import JsonStore
from kivy.uix.actionbar import ActionBar

from ddpclient import DDPClient


class BackendManager():

	subs = ['userData', 'budget', 'spending', 'savingsGoals']
	store = JsonStore('key.json')

	def __init__(self):
		self.ddp = DDPClient(self, "localhost", 3000)
		self.sm = ScreenManager(transition=NoTransition())
		self.login = LoginScreen(name="Login")
		self.login.set_ddp_manager(self)
		self.main_screen = MainScreen(name="Main")
		self.main_screen.set_ddp_manager(self)

		self.sm.add_widget(self.login)
		self.sm.add_widget(self.main_screen)

		self.subs_ready = 0
		self.dispatcher = {"login": self.notify_login}

	def start(self):
		self.ddp.connect()
		if "token" in self.store:
			self.token = self.store.get("token")['token']
			print "token:!!", self.token
			self.ddp.token_login(self.token)
		else:
			self.token = None

	def notify(self, method):
		if method in self.dispatcher:
			self.dispatcher[method]()

	def notify_login(self):
		#change screen to app, etc.
		self.store.put("token", token=self.token)
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


class DrActionBar(ActionBar):
	pass

class BigCircle(Widget):
	pass

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
	bigcircle = ObjectProperty(None)

	ddp_manager = None

	def set_ddp_manager(self, ddp_manager):
		self.ddp_manager = ddp_manager	

class MoneybagsApp(App):
	ddp_manager = None

	def on_start(self):
		self.ddp_manager.start()

	def on_stop(self):
		pass

	def on_pause(self):
		pass

	def on_resume(self):	
		pass

	def build(self):
		self.ddp_manager = BackendManager()
		return self.ddp_manager.sm

if __name__ == '__main__':
	MoneybagsApp().run()

'''
ActionBar:
			pos_hint: {'top': 1}
			background_color: (0,0,0,1)
			ActionView:
				title: 'Dr. Moneybags'''