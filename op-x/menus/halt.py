from ..menu import Menu, Option

class HaltMenu(Menu):
	name = "main"
	def halt(self):
		self.system.halt()
	def restart(self):
		self.system.restart()
	def __init__(self):
		super().__init__([
			Option("halt", self.halt),
			Option("restart", self.restart)
		])
	def select(self, option):
		option.value()
