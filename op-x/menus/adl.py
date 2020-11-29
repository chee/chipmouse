from ..controls import Control
import jack
from ..menu import Menu
from ..adl import AdlType, AdlProcess, Program

class AdlMenu(Menu):
	name = "adl"
	program = Program()
	right = Control.top_right
	left = Control.top_left
	process = AdlProcess(type=AdlType.adl)
	def select(self, _):
		pass
	def handle_control_down(self, control):
		super().handle_control_up(control)
		if control is self.right:
			self.program.inc()
			self.process.program_change(self.program.value())
		if control is self.left:
			self.program.dec()
			self.process.program_change(self.program.value())
	def quit(self):
		if self.process:
			self.process.stop()
		super().quit()

	def show(self):
		left = self.controls.name_for(self.left)
		right = self.controls.name_for(self.right)
		self.screen.text(
			f"""ADLmidi

press {left} and {right} to switch instrument.""")

	def start(self):
		self.process.start(error=lambda message: self.screen.error(message))

class OpnMenu(Menu):
	name = "opn"
	program = Program()
	right = Control.top_right
	left = Control.top_left
	process = AdlProcess(type=AdlType.opn)
	def select(self, _):
		pass
	def handle_control_down(self, control):
		super().handle_control_down(control)
		if control is self.right:
			self.program.inc()
			self.process.program_change(self.program.value())
		if control is self.left:
			self.program.dec()
			self.process.program_change(self.program.value())
	def quit(self):
		if self.process:
			self.process.stop()
		super().quit()

	def show(self):
		left = self.controls.name_for(self.left)
		right = self.controls.name_for(self.right)
		self.screen.text(
			f"""OPNmidi

press {left} and {right} to switch instrument.""")

	def start(self):
		self.process.start(error=lambda message: self.screen.error(message))
