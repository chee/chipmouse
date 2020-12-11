from abc import abstractmethod, ABCMeta
from enum import Enum
from signal import valid_signals
from threading import Thread
from time import sleep, time
from typing import Callable, List, Optional, Dict, Sequence, Tuple, Union
from .screen import Screen
from .system import System
from .controls import Controls, Control, Level
from typing import TypeVar, Generic
import threading
import numpy

OptionValue = TypeVar('OptionValue')

class Option(Generic[OptionValue]):
	def __init__(self, name: str, value: OptionValue):
		self.name = name
		self.value: OptionValue = value

class MenuValue(Option, Generic[OptionValue]):
	def __init__(self, name: str,
		     color: Tuple[int, int, int],
		     seq: Sequence[OptionValue],
		     initial = 0,
		     step=10,
		     finestep=1,
		     callback=lambda _:_):
		self.name = name
		self.seq = seq
		self.index = initial
		self.step = step
		self.finestep = finestep
		self.color = color
		self.callback = callback
	@property
	def value(self) -> OptionValue:
		 return self.seq[self.index]
	@property
	def max(self):
		return len(self.seq) - 1
	def inc(self, fine=False):
		self.index += self.finestep if fine else self.step
		if self.index > self.max:
			self.index = self.max
		self.announce()
	def dec(self, fine=False):
		self.index -= self.finestep if fine else self.step
		if self.index < 0:
			self.index = 0
		self.announce()
	def set(self, index):
		self.index = index
		self.announce()
	def announce(self):
		self.callback(self.value)

class Menu(metaclass=ABCMeta):
	has_submenu = False
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
		return [option.name for option in self.options]
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
		self.controls.take(self.handle_control,
				   has_submenu=self.has_submenu)
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

class ValueMenu(Menu):
	options: List[MenuValue]
	has_submenu = True
	def __init__(self, options: Optional[List[MenuValue]] = None):
		self.options = options or []
		self.active = 0
	def register(self, mv: MenuValue):
		self.options.append(mv)
		self.show()
	def inc_active_option(self, fine=False):
		active = self.active_option
		if not active:
			return
		if isinstance(active, MenuValue):
			active.inc(fine)
	def dec_active_option(self, fine=False):
		active = self.active_option
		if not active:
			return
		if isinstance(active, MenuValue):
			active.dec(fine)
	def handle_control(self, control):
		if control is Control.top_right:
			self.inc_active_option()
			self.show()
		if control is Control.top_left:
			self.dec_active_option()
			self.show()
		if control is Control.submenu_right:
			self.inc_active_option(fine=True)
			self.show()
		if control is Control.submenu_left:
			self.dec_active_option(fine=True)
			self.show()
		super().handle_control(control)
	def show(self):
		self.screen.value_menu(values=self.options,
				       active=self.active_name)
	def clear(self):
		self.options = []

class MenuColor(Enum):
	first = (0, 150, 250)
	second = (10, 250, 120)
	third = (255, 255, 255)
	fourth = (250, 180, 0)


class FourValueMenu(ValueMenu):
	colors = {}
	sine_menus: Dict[str, "SineMenu"] = {}
	def __getitem__(self, name):
		return self.colors[name]
	def __setitem__(self, name, value):
		self.colors[name] = value
	def register(self,
		     name: str,
		     color: MenuColor,
		     seq: Sequence,
		     initial: int,
		     step: int,
		     finestep: int,
		     callback: Callable):
		menu_value = MenuValue(name=name,
				       color=color.value,
				       seq=seq,
				       initial=initial,
				       step=step,
				       finestep=finestep,
				       callback=callback)
		self.sine_menus[name] = SineMenu(menu_value)
		self.sine_menus[name].parent = self
		super().register(menu_value)
		self[menu_value.name] = menu_value
		self[color.name] = menu_value
	def start(self):
		for menu_color in ["first", "second", "third", "fourth"]:
			try:
				self.__getitem__(menu_color)
			except:
				raise RuntimeError(f"You must register all four mvs. missing: {menu_color}")
		super().start()
	def select(self, option):
		sm = self.sine_menus[option.name]
		sm.start()
		sm.take_control()
		sm.show()
		sm.thread = Thread(target=sm.loop)
		sm.thread.start()
	def quit(self):
		self.colors.clear()
		for _, menu in self.sine_menus.items():
			menu.looping = False
		self.sine_menus.clear()
		self.clear()
		super().quit()

class SineMenu(FourValueMenu):
	mode = "set"
	looping = False
	thread: Optional[Thread] = None
	time = 0
	def __init__(self, menu_value: MenuValue):
		self.menu_value = menu_value
		super().__init__()
	def set_mode(self, mode):
		self.mode = mode
	def start(self):
		if len(self.options):
			super().start()
			return
		self.register("mode",
			      MenuColor.first,
			      ["set", "sine"],
			      step=1,
			      finestep=1,
			      initial=0,
			      callback=self.set_mode)
		self.register("sine_freq",
			      MenuColor.second,
			      numpy.arange(0.01, 40.0, 0.01),
			      step=10,
			      finestep=1,
			      initial=1,
			      callback=self.set_speed)
		self.register("sine_start",
			      MenuColor.third,
			      range(self.menu_value.max + 1),
			      step=10,
			      finestep=1,
			      initial=0,
			      callback=self.set_start)
		self.register("sine_end",
			      MenuColor.fourth,
			      range(self.menu_value.max + 1),
			      step=10,
			      finestep=1,
			      initial=self.menu_value.max,
			      callback=self.set_end)
		super().start()
	def set_speed(self, speed):
		#self.sspeed = speed
		pass
	def set_start(self, start):
		#self.sstart = start
		pass
	def set_end(self, end):
		#self.send = end
		pass
	def next(self):
		value = self.menu_value.value
		if self.mode == "set":
			return value
		if self.mode == "sine":
			freq = self.colors["sine_freq"]
			max = self.menu_value.max
			granules = max * 2
			sleeptime = 0.001
			sleep(sleeptime)
			self.time = self.time + (freq/granules) + (sleeptime*freq*1000)
			signal = numpy.sin(2 * numpy.pi * self.time / granules)
			value = (signal + 1) * (max / 2)
			return int(value)
	def loop(self):
		self.looping = True
		previous = None
		while self.looping:
			if self.mode == "set":
				continue
			value = self.next()
			if value != previous:
				self.menu_value.set(value)
				previous = value
	def quit(self):
		# our parents will kill us when it's time for them to die
		#self.looping = False
		Menu.quit(self)



class MenuWithSubmenus(Menu):
	def __init__(self, submenus: Optional[List[Menu]] = None):
		options = []
		if submenus:
			for menu in submenus:
				menu.parent = self
				options.append(Option(menu.name, menu))
		super().__init__(list(options))

	def select(self, option):
		option.value.start()
		option.value.show()
		option.value.take_control()
