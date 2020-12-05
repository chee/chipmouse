from typing import Optional
from ..menu import ValueMenu
from ..menu import CyanMenuValue, YellowMenuValue, GreenMenuValue, BlueMenuValue
from ..jack_client import JackClient
import numpy as np
import operator

def m2f(note):
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

class Synth(JackClient):
	jack_client_name = "chipmouse.ynth"
	NOTEON = 0x9
	NOTEOFF = 0x8
	notes = []
	frequency = 440.0
	playing = False
	detune = 0.9
	factor = 2.0
	_op = operator.add
	@property
	def fm(self):
		return self.frequency - self.detune
	def __init__(self):
		self.register_jack_client(midi_in=["keys"], audio_out=["sounds"])
		self.connect_speakers_to(self.audio_out)
		self.connect_all_midi_to(self.midi_in)
	def quit(self):
		self.deactivate_jack_client()
	def jack_process_callback(self, blocksize):
		for offset, data in self.midi_in[0].incoming_midi_events():
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

		buf = self.audio_out[0].get_array()
		buf.fill(0)
		t = (np.arange(blocksize) + self.jack_client.last_frame_time) / self.samplerate
		carrier = np.sin(2 * np.pi * self.frequency * t)
		mod = np.sin(2 * np.pi * (self.fm * self.factor) * t)
		signal = np.cos(carrier + mod)
		if self.playing:
			buf += signal

class SynthMenu(ValueMenu):
	name = "synth"
	cyan = CyanMenuValue("dogness", 50)
	yellow = YellowMenuValue("wideness", 2)
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
	def cyan_change(self):
		self.synth.factor = self.cyan.value / 25
		pass
	def yellow_change(self):
		self.synth.detune = self.yellow.value / 20
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