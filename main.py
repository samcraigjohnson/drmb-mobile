import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class LoginScreen(Widget):
	f_username = ObjectProperty(None)
	f_password = ObjectProperty(None)

	def login(self):
		uname = self.f_username.text
		pwd = self.f_password.text
		print uname, pwd

class MoneybagsApp(App):

	def build(self):
		return LoginScreen()

if __name__ == '__main__':
	MoneybagsApp().run()