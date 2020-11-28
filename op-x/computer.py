from .mode import Mode
from tkinter import Tk

class Computer():
	def __init__(self, mode):
		if mode is not Mode.COMPUTER:
			raise RuntimeError("only computers can use Computers")

		self.root = Tk()
