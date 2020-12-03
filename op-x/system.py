from .screen import Screen
from .mode import Mode
from os import system

class System:
	def __init__(self, mode, screen: Screen):
		self.mode = mode
		self.screen = screen
		if mode == Mode.PI:
			system("systemctl start --user a2jmidid")
	def halt(self):
		self.screen.file("shutdown.png")
		if self.mode == Mode.PI:
			system("sudo halt")
		if self.mode == Mode.COMPUTER:
			print("imagine if i actually shut down lol")
	def restart(self):
		self.screen.menu(options=[
			"i am restarting:",
			"- jackd",
			"- op-x"
		], active="")
		if self.mode == Mode.PI:
			system("systemctl restart --user jackd")
			system("systemctl restart --user op-x")
		if self.mode == Mode.COMPUTER:
			print("if you were a pi, jackd and a2jmidid and op-x would have been restarten")
