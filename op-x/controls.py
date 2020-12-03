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
	menu_active = 'menu_active'
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
				io.add_event_detect(pin, io.BOTH, lambda pin: self.gpio(pin), bouncetime=1000)
		if mode is Mode.COMPUTER:
			from . import tkroot
			tkroot.bind("<KeyPress>", self.key_down)
			tkroot.bind("<KeyRelease>", self.key_up)
	def name_for(self, control: Control):
		names = self.names[self.mode]
		if control in names:
			return names[control]
		if control is Control.menu_exit:
			return f"{names[Control._bottom_right]} and {names[Control.top_left]}"
		if control is Control.menu_yes:
			return f"{names[Control._bottom_right]} and {names[Control.top_right]}"
		if control is Control.menu_next:
			return f"{names[Control._bottom_right]} and {names[Control.bottom_left]}"
	def key_down(self, key):
		if key.char in self.keys:
			self.down(self.keys[key.char])
	def key_up(self, key):
		if key.keysym in self.keys:
			self.up(self.keys[key.keysym])
	def gpio(self, pin: int):
		control = self.buttons[pin]
		io = self.io
		state = io.input(pin)
		if state == io.HIGH:
			self.up(control)
		else:
			self.down(control)
	def down(self, control: Control):
		if control is Control._bottom_right:
			self.level = Level.menu
			if self.down_callback:
				self.down_callback(Control.menu_active)
		elif self.level is Level.menu:
			if control is Control.top_left:
				self.down_callback(Control.menu_exit)
			if control is Control.top_right:
				self.down_callback(Control.menu_yes)
			if control is Control.bottom_left:
				self.down_callback(Control.menu_next)
			elif self.down_callback:
				self.down_callback(control)
	def up(self, control: Control):
		if control is Control._bottom_right and self.level is Level.menu:
			self.level = Level.default
			if self.up_callback:
				self.up_callback(Control.menu_active)
		if self.up_callback is None:
			return
		else:
			self.up_callback(control)
	def take(self, down_callback, up_callback):
		self.down_callback = down_callback
		self.up_callback = up_callback
