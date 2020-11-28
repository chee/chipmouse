from abc import abstractmethod, abstractproperty, ABCMeta
from typing import Any, List, Dict, Optional
from .view import View
from .mode import Mode
from .screen import Screen
from .controls import Controls, Control

class Option():
	def __init__(self, name, value):
		self.name = name
		self.value = value

class Menu(metaclass=ABCMeta):
	parent: Optional['Menu'] = None
	_screen: Optional[Screen] = None
	_controls: Optional[Controls] = None

	@property
	@abstractmethod
	def name(self):
		pass

	@property
	def screen(self):
		if self._screen:
			return self._screen
		elif self.parent:
			return self.parent.screen
		else:
			raise RuntimeError("no parent, no screen")

	@property
	def controls(self):
		if self._controls:
			return self._controls
		elif self.parent:
			return self.parent.controls
		else:
			raise RuntimeError("no parents and no controls")

	def __init__(self, options: List[Option]):
		self.options = options
		self.active = 0

	def set_platform(self, screen, controls):
		self._screen = screen
		self._controls = controls

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
		if control is Control.menu_next:
			self.inc()
			self.show()
		if control is Control.menu_exit:
			self.quit()
		if control is Control.menu_yes:
			self.select(self.options[self.active])
	def option_names(self):
		return map(lambda o : o.name, self.options)
	def active_name(self):
		return self.options[self.active].name
	def subscribe(self):
		self.controls.subscribe(None, self.handle_control)
	def show(self):
		self.screen.menu(options=self.option_names(),
				 active=self.active_name())
	@abstractmethod
	def select(self, option):
		pass

	def quit(self):
		if self.parent:
			self.controls.unsubscribe()
			self.parent.subscribe()
			self.parent.show()
