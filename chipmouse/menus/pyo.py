from ..controls import Control
from ..menu import Menu, Option, MenuWithSubmenus, ValueMenu
from ..menu import BlueMenuValue, GreenMenuValue, WhiteMenuValue, OrangeMenuValue
import pyo
from pyo import *
from random import random

class Synth:
	def __init__(self, transpo=1, mul=1):
		# Transposition factor.
		self.transpo = Sig(transpo)
		# Receive midi notes, convert pitch to Hz and manage 10 voices of polyphony.
		self.note = Notein(poly=10, scale=1, first=0, last=127)

		# Handle pitch and velocity (Notein outputs normalized amplitude (0 -> 1)).
		self.pit = self.note["pitch"] * self.transpo
		self.amp = MidiAdsr(self.note["velocity"], attack=0.001, decay=0.1, sustain=0.7, release=1, mul=0.1,)

		# Anti-aliased stereo square waves, mixed from 10 streams to 1 stream
		# to avoid channel alternation on new notes.
		self.osc1 = LFO(self.pit, sharp=0.5, type=2, mul=self.amp).mix(1)
		self.osc2 = LFO(self.pit * 0.997, sharp=0.5, type=2, mul=self.amp).mix(1)

		# Stereo mix.
		self.mix = Mix([self.osc1, self.osc2], voices=2)

		# High frequencies damping.
		self.damp = ButLP(self.mix, freq=5000)

		# Moving notches, using two out-of-phase sine wave oscillators.
		self.lfo = Sine(0.2, phase=[random(), random()]).range(250, 4000)
		self.notch = ButBR(self.damp, self.lfo, mul=mul)

	def out(self):
		"Sends the synth's signal to the audio output and return the object itself."
		self.notch.out()
		return self

	def sig(self):
		"Returns the synth's signal for future processing."
		return self.notch

class PyoSynthMenu(ValueMenu):
	name = "synth"
	blue = BlueMenuValue("dogness", 0)
	green = GreenMenuValue("wideness", 0)
	orange = OrangeMenuValue("averageness", 0)
	white = WhiteMenuValue("amount", 20)
	def __init__(self):
		self.blue.sub(self.blue_change)
		self.blue.sub(self.green_change)
		self.orange.sub(self.orange_change)
		self.blue.sub(self.white_change)
		super().__init__(options=[
			self.blue,
			self.green,
			self.orange,
			self.white
		])
	def start(self):
		try:
			server = self.server = Server(duplex=0)
		except:
			print("ERROR: i'm sure it's fine.")
		if not self.server:
			return
		server.setMidiInputDevice(99)
		server.boot()

		# Create the midi synth.
		self.synth = Synth()

		# Send the synth's signal into a reverb processor.
		self.rev = STRev(self.synth.sig(), inpos=[0.1, 0.9], revtime=2, cutoff=4000, bal=0.15).out()

		# It's very easy to double the synth sound!
		# One octave lower and directly sent to the audio output.
		self.synth2 = Synth(transpo=0.5, mul=0.7).out()
	def blue_change(self):
		self.synth.osc1._sharp = self.blue.value / 100
	def green_change(self):
		self.synth.osc1._sharp = self.green.value / 100
	def white_change(self):
		self.synth.lfo.range(self.white.value, self.white.value * self.blue.value)
	def orange_change(self):
		self.synth.lfo.range(self.orange.value, self.orange.value * self.orange.value)
	def quit(self):
		self.server.shutdown()
		del self.server
	def select(self, option):
		pass

class PyoMenu(MenuWithSubmenus):
	name = "pyo"
	def __init__(self):
		super().__init__([
			PyoSynthMenu()
		])
	def start(self):
		pass
