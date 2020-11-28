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
	def select(self):
		pass
	def handle_control(self, control):
		super().handle_control(control)
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
		controls = self.controls
		screen = self.screen
		screen.text(f"ADLmidi.\npress {controls.name_for(self.left)} and {controls.name_for(self.right)} to switch instrument.")
		self.process.start(error=lambda message: screen.error(message))
		self.subscribe()

class OpnMenu(Menu):
	name = "opn"
	program = Program()
	right = Control.top_right
	left = Control.top_left
	process = AdlProcess(type=AdlType.opn)
	def select(self):
		pass
	def handle_control(self, control):
		super().handle_control(control)
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
		controls = self.controls
		screen = self.screen
		screen.text(f"ADLmidi.\npress {controls.name_for(self.left)} and {controls.name_for(self.right)} to switch instrument.")
		self.process.start(error=lambda message: screen.error(message))
		self.subscribe()
