from typing import Optional
import jack
from time import sleep
from .jack_client import JackClient, name_or_alias_contains
from enum import Enum

class Op1Status(JackClient):
	jack_client_name = "chipmouse.op1watcher"
	def start(self, error):
		self.register_jack_client()
	def stop(self):
		self.deactivate_jack_client()
	_input: Optional[jack.MidiPort] = None
	_output: Optional[jack.MidiPort] = None
	@property
	def input(self):
		if self._input:
			return self._input
		for port in self.jack_client.get_ports(is_midi=True, is_input=True):
			if name_or_alias_contains(port, "OP-1"):
				self._input = port
				return port
		return None
	@property
	def output(self):
		if self._output:
			return self._output
		for port in self.jack_client.get_ports(is_midi=True, is_input=False):
			if name_or_alias_contains(port, "OP-1"):
				self._output = port
				return port
		return None
	@property
	def connected(self):
		return self.input is not None
	def jack_process_callback(self, frame):
		pass

op1 = Op1Status()
