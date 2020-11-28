from typing import Any, List, Dict
from .view import View
from .mode import Mode
from .screen import Screen
from .controls import Controls, Control

class Option():
	def __init__(self, name, value):
		self.name = name
		self.value = value

class Menu():
	def __init__(self, mode: Mode, options: List[Option]):
		self.mode = mode
		self.options = options
		self.active = 0
		self.screen = Screen(mode)
		self.controls = Controls(mode)
		self.controls.subscribe(None, self.handle_control)
	def inc(self):
		number_of_options = len(self.options)
		if self.active >= number_of_options - 1:
			self.active = 0
		else:
			self.active += 1
	def dec(self):
		number_of_options = len(self.options)
		if self.active <= 0:
			self.active = number_of_options - 1
		else:
			self.active -= 1
	def handle_control(self, control):
		print("hello")
		print(control)
		if control is Control.menu_next:
			self.inc()
			self.show()
	def option_names(self):
		return map(lambda o : o.name, self.options)
	def active_name(self):
		return self.options[self.active].name
	def show(self):
		if self.mode is Mode.PI:
			self.screen.clear()
		self.screen.menu(options=self.option_names(),
				 active=self.active_name())
	def select(self, option):
		return option


class MainMenu(Menu):
	def __init__(self, mode: Mode, views: List[View]):
		# options = map(lambda v: Option(v.name, v), views)
		options = [
			Option("coffee", None),
			Option("tea", None),
			Option("mackerel", None),
		]
		super().__init__(mode, list(options))
	def select(self, view):
		view.start()
