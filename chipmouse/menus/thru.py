from typing import Optional
from ..menu import Option, Menu
from ..jack_client import JackClient

class Thru(JackClient):
	jack_client_name = "chipmouse.thru"
	def start(self):
		self.register_jack_client()
		ins = self.jack_client.get_ports(is_midi=True, is_input=True)
		self.connect_all_midi_to(ins)
	def jack_process_callback(self, frame):
		pass
	def quit(self):
		self.deactivate_jack_client()

class ThruMenu(Menu):
	name = "MIDITHRU"
	def __init__(self):
		super().__init__()
		print("i will connect everything.")
	def start(self):
		self.thru = Thru()
		self.thru.start()
	def quit(self):
		self.thru.quit()
		super().quit()
	def select(self, option):
		pass
	def show(self):
		self.screen.text("XXXXXXXXXXXXX", color=(150, 250, 200))
