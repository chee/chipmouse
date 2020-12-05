from enum import Enum
from .mode import Mode

class Level(Enum):
	default = None
	menu = 'menu'

class Control(Enum):
	top_left = 'TL'
	top_right = 'TR'
	bottom_left = 'BL'
	_bottom_right = 'BR'
	menu_on = 'menu_on'
	menu_off = 'menu_off'
	menu_next = 'mnext'
	menu_yes = 'myes'
	menu_exit = 'mexit'

class Controls():
	level = Level.default
	down_callback = None
	up_callback = None
	names = {
		Mode.PI: {
			Control.top_left: 'a',
			Control.bottom_left: 'b',
			Control.top_right: 'x',
			Control._bottom_right: 'y',
		},
		Mode.COMPUTER: {
			Control.top_left: 'q',
			Control.bottom_left: 'a',
			Control.top_right: 'w',
			Control._bottom_right: 's',
		}
	}
	buttons = {
		5: Control.top_left,
		6:  Control.bottom_left,
		16: Control.top_right,
		24: Control._bottom_right
	}
	keys = {
		'q': Control.top_left,
		'w': Control.top_right,
		'a': Control.bottom_left,
		's': Control._bottom_right
	}
	def __init__(self, mode):
		self.mode = mode
		if mode is Mode.PI:
			import RPi.GPIO as io
			self.io = io
			buttons = self.buttons
			io.setmode(io.BCM)
			io.setup(list(buttons.keys()), io.IN, pull_up_down=io.PUD_UP)
			for pin, _ in buttons.items():
				io.add_event_detect(pin, io.FALLING, lambda pin: self.gpio(pin), bouncetime=50)
		if mode is Mode.COMPUTER:
			from . import tkroot
			tkroot.bind("<KeyRelease>", self.key)
	def key(self, key):
		if key.keysym in self.keys:
			self.press(self.keys[key.keysym])
	def gpio(self, pin: int):
		control = self.buttons[pin]
		self.press(control)
	def press(self, control: Control):
		if control is Control._bottom_right:
			if self.level == Level.default:
				self.level = Level.menu
				if self.callback:
					self.callback(Control.menu_on)
			else:
				self.level = Level.default
				if self.callback:
					self.callback(Control.menu_off)
		elif self.level is Level.menu:
			if control is Control.top_left:
				self.callback(Control.menu_exit)
			if control is Control.top_right:
				self.callback(Control.menu_yes)
			if control is Control.bottom_left:
				self.callback(Control.menu_next)
		elif self.callback:
			self.callback(control)
	def take(self, callback):
		self.callback = callback
