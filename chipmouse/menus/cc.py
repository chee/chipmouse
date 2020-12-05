from typing import Optional
from ..menu import FourValueMenu
from ..jack_client import JackClient
import numpy as np
from ..op1_status import op1
from queue import SimpleQueue

class CcMenu(FourValueMenu, JackClient):
	jack_client_name = "chipmouse.cc"
	name = "lfo"
	blue_name = "cc1"
	blue_default = 0
	green_name = "cc2"
	green_default = 47
	white_name = "cc3"
	white_default = 69
	orange_name = "cc4"
	orange_default = 85
	queue = SimpleQueue()
	offset = 0
	def start(self):
		self.register_jack_client(midi_out=["cc"])
		try:
			self.jack_client.connect(self.midi_out[0], op1.input)
		except:
			print("no connection to op1, check dot")
		super().start()
	def write(self, cc, val):
		event = [0xb0, cc, (((val * 126) // 100) + 1)]
		self.midi_out[0].write_midi_event(0, event)
		# self.queue.put(event)
	def blue_change(self):
		self.write(1, self.blue.value)
	def green_change(self):
		self.write(2, self.green.value)
	def white_change(self):
		self.write(3, self.white.value)
	def orange_change(self):
		self.write(4, self.orange.value)
	def quit(self):
		self.deactivate_jack_client()
		super().quit()
	def jack_process_callback(self, frame):
		pass
		# self.offset += frame
		# while self.offset > frame:
		#	self.offset -= frame
		# while self.queue.empty() is not True:
		#	msg = self.queue.get()
		#	self.midi_out[0].write_midi_event(
		#		self.offset,
		#		msg
		#	)
	def select(self, option):
		pass
