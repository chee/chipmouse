import jack
from time import sleep
from .jack_client import JackClient
from enum import Enum

class Op1Status(JackClient):
	jack_client_name = "chipmouse.op1watcher"
	def start(self, error):
		self.register_jack_client()
	def stop(self):
		self.deactivate_jack_client()
	@property
	def input(self):
		for port in self.jack_client.get_ports(is_midi=True, is_input=True):
			if "OP-1" in port.name:
				return port
		return None
	@property
	def output(self):
		for port in self.jack_client.get_ports(is_midi=True, is_input=False):
			if "OP-1" in port.name:
				return port
		return None
	@property
	def connected(self):
		for port in self.jack_client.get_ports(is_midi=True):
			if "OP-1" in port.name:
				return True
		return False
	def jack_process_callback(self, frame):
		pass

op1 = Op1Status()
