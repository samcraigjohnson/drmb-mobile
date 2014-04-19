import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class LoginScreen(Layout):
	f_username = ObjectProperty(None)
	f_password = ObjectProperty(None)

	def print_names(self, dt):
		print self.f_username, ":", self.f_password
	
class MoneybagsApp(App):

	def build(self):
		screen = LoginScreen()
		Clock.schedule_interval(screen.print_names, .5)
		return screen

if __name__ == '__main__':
	MoneybagsApp().run()