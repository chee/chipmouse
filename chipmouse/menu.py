from abc import abstractmethod, ABCMeta
from typing import List, Optional, Dict
from .screen import Screen
from .system import System
from .controls import Controls, Control, Level
from typing import TypeVar, Generic

OptionValue = TypeVar('OptionValue')

class Option(Generic[OptionValue]):
	def __init__(self, name: str, value: OptionValue):
		self.name = name
		self.value: OptionValue = value

class MenuValue(Option, Generic[OptionValue]):
	subs = []
	def __init__(self, name: str, color, default = 0):
		self.name = name
		self.value: OptionValue = default
		self.color = color
	def inc(self, fine=False):
		self.value += 1 if fine else 10
		if self.value > 100:
			self.value = 100
		self.announce()
	def dec(self, fine=False):
		self.value -= 1 if fine else 10
		if self.value < 0:
			self.value = 0
		self.announce()
	def sub(self, fn):
		self.subs.append(fn)
		return lambda : self.subs.remove(fn)
	def announce(self):
		for fn in self.subs:
			fn()

class Menu(metaclass=ABCMeta):
	parent: Optional['Menu'] = None
	_screen: Optional[Screen] = None
	_controls: Optional[Controls] = None
	_system: Optional[System] = None
	name = "abstract menu"

	@property
	def system(self):
		if self._system:
			return self._system
		elif self.parent:
			return self.parent.system
		else:
			raise RuntimeError("no parent, no system")

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

	def __init__(self, options: Optional[List[Option]] = None):
		self.options = options
		self.active = 0

	def set_platform(self, screen, controls, system):
		self._screen = screen
		self._controls = controls
		self._system = system

	def inc(self):
		if not self.options:
			return
		number_of_options = len(self.options)
		if self.active >= number_of_options - 1:
			self.active = 0
		else:
			self.active += 1
	def dec(self):
		if not self.options:
			return
		number_of_options = len(self.options)
		if self.active <= 0:
			self.active = number_of_options - 1
		else:
			self.active -= 1
	def handle_control(self, control):
		if control is Control.menu_on:
			self.screen.overlay_menu_hint()
		if control is Control.menu_off:
			self.screen.remove_menu_hint()
		if control is Control.menu_next:
			self.inc()
			self.show()
			self.screen.overlay_menu_hint()
		if control is Control.menu_exit:
			self.quit()
			self.screen.overlay_menu_hint()
		if control is Control.menu_yes:
			self.screen.overlay_menu_hint()
			self.select(self.active_option)
	def option_names(self):
		if not self.options:
			return None
		return map(lambda o : o.name, self.options)
	@property
	def active_option(self):
		if self.options:
			return self.options[self.active]
		else:
			return None
	@property
	def active_name(self):
		if self.active_option:
			return self.active_option.name
	@property
	def active_value(self):
		if self.active_option:
			return self.active_option.value
	def take_control(self):
		self.controls.take(self.handle_control)
	def show(self):
		self.screen.menu(options=self.option_names(),
				 active=self.active_name)
	def start(self):
		pass

	def select(self, option):
		pass

	def quit(self):
		if self.parent:
			self.parent.show()
			self.parent.take_control()

class CyanMenuValue(MenuValue):
	def __init__(self, name, default=0):
		super().__init__(name=name, color=(0, 200, 250), default=default)

class YellowMenuValue(MenuValue):
	def __init__(self, name, default=0):
		super().__init__(name=name, color=(250, 230, 80), default=default)

class GreenMenuValue(MenuValue):
	def __init__(self, name, default=0):
		super().__init__(name=name, color=(0, 250, 150), default=default)

class BlueMenuValue(MenuValue):
	def __init__(self, name, default=0):
		super().__init__(name=name, color=(30, 130, 250), default=default)

class ValueMenu(Menu):
	fine = False
	options: List[MenuValue]
	def __init__(self, options: List[MenuValue]):
		self.options = options
		self.active = 0
		for menu_value in options:
			menu_value.sub(self.show)
	def inc_active_option(self):
		av = self.active_option
		if not av:
			return
		if isinstance(av, MenuValue):
			av.inc(fine=self.fine)
	def dec_active_option(self):
		av = self.active_option
		if not av:
			return
		if isinstance(av, MenuValue):
			av.dec(fine=self.fine)
	def handle_control(self, control):
		super().handle_control(control)
		if control is Control.bottom_left and self.controls.level is not Level.menu:
			self.fine = True
		if control is Control.top_right:
			self.inc_active_option()
		if control is Control.top_left:
			self.dec_active_option()
		if control is Control.bottom_left:
			self.fine = False
	def show(self):
		self.screen.value_menu(values=self.options,
				       active=self.active_name)


class FourValueMenu(ValueMenu):
	cyan_name = "cyan"
	yellow_name = "yellow"
	blue_name = "blue"
	green_name = "green"
	cyan_default = 0
	yellow_default = 0
	blue_default = 0
	green_default = 0
	def cyan_change(self):
		pass
	def yellow_change(self):
		pass
	def blue_change(self):
		pass
	def green_change(self):
		pass
	def __init__(self):
		self.cyan = CyanMenuValue(
			self.cyan_name, self.cyan_default)
		self.yellow = YellowMenuValue(
			self.yellow_name, self.yellow_default)
		self.blue = BlueMenuValue(
			self.blue_name, self.blue_default)
		self.green = GreenMenuValue(
			self.green_name, self.green_default)
		self.cyan.sub(self.cyan_change)
		self.yellow.sub(self.yellow_change)
		self.blue.sub(self.blue_change)
		self.green.sub(self.green_change)
		super().__init__(options=[
			self.cyan,
			self.yellow,
			self.blue,
			self.green
		])


class MenuWithSubmenus(Menu):
	def __init__(self, submenus: List[Menu]):
		options = []
		for menu in submenus:
			menu.parent = self
			options.append(Option(menu.name, menu))
		super().__init__(list(options))

	def select(self, option):
		option.value.start()
		option.value.show()
		option.value.take_control()
