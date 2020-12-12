from typing import Optional

from jack import OwnMidiPort
from ..menu import FourValueMenu, MenuColor
from ..jack_client import JackClient
import numpy as np
from ..op1_status import op1

class CcMenu(FourValueMenu, JackClient):
	jack_client_name = "chipmouse.lfo"
	name = "lfo"
	queue = []
	last_event = None
	outport: Optional[OwnMidiPort] = None
	def start(self):
		self.register_jack_client(midi_out=["cc"])
		self.outport = self.midi_out[0]
		try:
			self.jack_client.connect(self.outport, op1.input)
		except:
			print("no connection to op1, check dot")
		self.register("cc1",
			      MenuColor.first,
			      range(0, 127),
			      step=10,
			      finestep=1,
			      initial=20,
			      callback=lambda val: self.write(1, val))
		self.register("cc2",
			      MenuColor.second,
			      range(0, 127),
			      step=10,
			      finestep=1,
			      initial=47,
			      callback=lambda val: self.write(2, val))
		self.register("cc3",
			      MenuColor.third,
			      range(0, 127),
			      step=10,
			      finestep=1,
			      initial=69,
			      callback=lambda val: self.write(3, val))
		self.register("cc4",
			      MenuColor.fourth,
			      range(0, 127),
			      step=10,
			      finestep=1,
			      initial=100,
			      callback=lambda val: self.write(4, val))
		super().start()
	def write(self, cc, val):
		event = [0xb0, cc, val]
		self.queue.append(event)
		self.last_event = event
	def jack_process_callback(self, _frame):
		if not self.outport:
			return
		self.outport.clear_buffer()
		events = list(self.queue)
		self.queue.clear()
		for index, event in enumerate(events):
			event = events[index]
			if len(event):
				self.outport.write_midi_event(index, event)
