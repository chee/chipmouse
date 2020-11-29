from ..controls import Control
from typing import List, Optional
from ..menu import Menu, Option, MenuWithSubmenus
from subprocess import Popen

class SpeakMenu(Menu):
	name = "speak"
	text = " "
	chars = " .abcdefghijklmnopqrstuvwxyz"
	process: Optional[Popen] = None
	def __init__(self):
		super().__init__([
			Option("default", ["espeak"]),
			Option("mimic default", ["mimic", "-t"]),
			Option("mimic awb", ["mimic", "-voice", "awb", "-t"]),
			Option("mimic rms", ["mimic", "-voice", "rms", "-t"]),
			Option("mimic slt", ["mimic", "-voice", "slt", "-t"])
		])
	def show(self):
		self.screen.text(self.text + "|")
	def start(self):
		self.text = " "
	def handle_control_up(self, control):
		super().handle_control_up(control)
		if control is Control.menu_next:
			self.screen.overlay_text(" ".join(self.active_value or []))
		if control is Control.bottom_left:
			char = self.text[-1]
			next = self.chars.find(char) + 1
			if next >= len(self.chars):
				next = 0
			self.text = self.text[:-1] + self.chars[next]
			self.show()
		if control is Control.top_right:
			self.text += " "
			cmd = self.active_value
			if cmd and isinstance(cmd, list): # for the types
				if self.process:
					self.process.kill()
				self.process = Popen(args=cmd + [self.text])
			self.show()
		if control is Control.top_left:
			self.text = self.text[:-1]
			self.show()
