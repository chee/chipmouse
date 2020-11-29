from typing import Optional
from ..controls import Control
from ..menu import Menu, Option, MenuWithSubmenus, ValueMenu
from ..menu import CyanMenuValue, YellowMenuValue, GreenMenuValue, BlueMenuValue
import jack
import numpy as np
import operator
import math

def m2f(note):
	print(2 ** ((note - 69) / 12) * 440)
	return 2 ** ((note - 69) / 12) * 440

class Voice:
	def __init__(self, pitch, fs, attack, release):
		self.fs = fs
		self.attack = attack
		self.release = release
		self.time = 0
		self.time_increment = m2f(pitch) / fs
		self.weight = 0

		self.target_weight = 0
		self.weight_step = 0
		self.compare = None

	def trigger(self, vel):
		if vel:
			dur = self.attack * self.fs
		else:
			dur = self.release * self.fs
		self.target_weight = vel / 127
		self.weight_step = (self.target_weight - self.weight) / dur
		self.compare = operator.ge if self.weight_step > 0 else operator.le

	def update(self):
		"""Increment weight."""
		if self.weight_step:
			self.weight += self.weight_step
			if self.compare(self.weight, self.target_weight):
				self.weight = self.target_weight
				self.weight_step = 0

class Synth():
	NOTEON = 0x9
	NOTEOFF = 0x8
	attack = 0.01
	release = 0.2
	fs = 0
	client: Optional[jack.Client] = None
	notes = []
	frequency = 440
	playing = False
	@property
	def outport(self) -> jack.OwnPort:
		return self.client.outports[0]
	@property
	def inport(self) -> jack.OwnMidiPort:
		return self.client.midi_inports[0]
	def __init__(self):
		client = self.client = jack.Client("op-x")
		client.midi_inports.register("operator")
		client.outports.register(f"notes")
		midi_out = client.get_ports(is_midi=True, is_input=False)
		speakers = client.get_ports(is_physical=True, is_input=True, is_audio=True)

		self.op1_out = None

		for port in midi_out:
			if "OP-1" in port.name:
				self.op1_out = port
				break

		self.client.connect(self.op1_out, self.inport)
		for speaker in speakers:
			client.connect(self.outport, speaker)

		client.set_samplerate_callback(self.samplerate)
		client.set_process_callback(self.process)
		client.activate()
	def quit(self):
		self.client.deactivate()
	def process(self, blocksize):
		for offset, data in self.inport.incoming_midi_events():
			if len(data) == 3:
				status, pitch, vel = bytes(data)
				# MIDI channel number is ignored!
				status >>= 4
				if status == self.NOTEON and vel > 0:
					self.frequency = m2f(pitch)
					self.notes.append(pitch)
					self.playing = True
				elif status in (self.NOTEON, self.NOTEOFF):
					self.notes.remove(pitch)
					if len(self.notes) > 0:
						if self.frequency == m2f(pitch):
							self.frequency = m2f(self.notes[-1])
					else:
						self.playing = False
				else:
					pass  # ignore
			else:
				pass  # ignore

		buf = self.outport.get_array()
		buf.fill(0)
		t = (np.arange(blocksize) + self.client.last_frame_time) / self.fs
		signal = np.sin(2 * np.pi * self.frequency * t)
		if self.playing:
			buf += signal / 127

	def samplerate(self, samplerate):
		self.fs = samplerate

class SynthMenu(ValueMenu):
	name = "synth"
	cyan = CyanMenuValue("dogness", 0)
	yellow = YellowMenuValue("wideness", 0)
	blue = BlueMenuValue("averageness", 0)
	green = GreenMenuValue("amount", 20)
	synth: Optional[Synth] = None
	def __init__(self):
		# TODO rewrite 'ValueMenu' to expect cyan, yellow, blue and
		# green to be defined and then do all of this automatically
		# (or create a FourValueMenu that does this)
		self.cyan.sub(self.cyan_change)
		self.yellow.sub(self.yellow_change)
		self.blue.sub(self.blue_change)
		self.green.sub(self.green_change)
		super().__init__(options=[
			self.cyan,
			self.yellow,
			self.blue,
			self.green
		])
	def start(self):
		self.synth = Synth()
		print(self.synth)
	def cyan_change(self):
		pass
	def yellow_change(self):
		pass
	def green_change(self):
		pass
	def blue_change(self):
		pass
	def quit(self):
		self.synth.quit()
		super().quit()
	def select(self, option):
		pass
