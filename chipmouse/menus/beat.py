from mido.midifiles.tracks import MidiTrack
from ..controls import Control
import jack
from ..menu import Menu, Option
from ..jack_client import JackClient
from mido import MidiFile, MidiTrack, Message, bpm2tempo
from ..op1_status import op1
from random import randint, choice, randrange
import binascii
from time import time

HAT = 61

def major(note):
	return [note, note + 4, note + 7]

def minor(note):
	return [note, note + 4, note + 7]

class BeatMenu(Menu, JackClient):
	name = "beats"
	jack_client_name = "chipmouse.beat"
	next = Control.bottom_left
	prev = Control.top_left
	mid = None
	offset = 0
	beat = 0
	msg = None
	def __init__(self):
		super().__init__([
			Option("HAT-hat", self.one),
			Option("hat?hat?hat", self.two),
			Option("CHR", self.three)
		])
		self.op1 = op1
	def one(self):
		self.midifile = MidiFile()
		track = MidiTrack()
		self.midifile.tracks.append(track)
		track.append(Message("note_on", note=HAT, velocity=127, time=0))
		track.append(Message("note_off", note=HAT, velocity=127, time=32))
		track.append(Message("note_on", note=HAT, velocity=64, time=64))
		track.append(Message("note_off", note=HAT, velocity=64, time=96))
		self.mid = iter(self.midifile)
		self.msg = next(self.mid)
	def two(self):
		self.midifile = MidiFile()
		track = MidiTrack()
		self.midifile.tracks.append(track)
		track.append(Message("note_on", note=HAT, velocity=127, time=0))
		track.append(Message("note_off", note=HAT, velocity=127, time=32))
		track.append(Message("note_on", note=HAT, velocity=randint(0, 127), time=64))
		track.append(Message("note_off", note=HAT, velocity=64, time=96))
		self.mid = iter(self.midifile)
		self.msg = next(self.mid)
	def three(self):
		self.midifile = MidiFile()
		track = MidiTrack()
		self.midifile.tracks.append(track)
		roots = [48, 50, 52, 53, 55, 57, 59, 60]
		for time in range(0, 1025, 32):
			if randint(0, 20) > 15:
				continue
			for note in major(choice(roots)):
				track.append(Message("note_on", note=note, velocity=randint(63, 100), time=time))
				off_time = randrange(0, 129, 32)
				track.append(Message("note_off", note=note, velocity=127, time=off_time))
		self.mid = iter(self.midifile)
		self.msg = next(self.mid)
	def show(self):
		names = list(self.option_names())
		self.screen.menu(options=names,
				 active=self.active_name)
	def handle_control(self, control):
		super().handle_control(control)
		if control is self.next:
			self.inc()
			self.show()
		if control is self.prev:
			self.dec()
			self.show()
		self.active_value()
	def quit(self):
		self.deactivate_jack_client()
		super().quit()
	last_beat_time = 0
	def jack_process_callback(self, frame):
		for offset, data in self.midi_in[0].incoming_midi_events():
			event = binascii.hexlify(data).decode()
			if event == "f8":
				print(offset)
				print(time() - self.last_beat_time)
				self.last_beat_time = time()
				# print("beat", self. beat)
		port = self.midi_out[0]
		if not self.mid:
			return
		if self.msg is None:
			self.active_value()
		port.clear_buffer()
		while True:
			if self.offset >= frame:
				self.offset -= frame
				return
			port.write_midi_event(self.offset, self.msg.bytes())
			try:

				self.msg = next(self.mid)
			except StopIteration:
				self.msg = None
				return
			self.offset += round(self.msg.time * self.samplerate)
	def start(self):
		self.register_jack_client(midi_in=["clock"], midi_out=["beat"])
		try:
			self.jack_client.connect(self.op1.output, self.midi_in[0])
		except:
			print("didn't connect in to out")
		try:
			self.jack_client.connect(self.midi_out[0], self.op1.input)
		except:
			print("didn't connect out to in")
		# self.connect_all_midi_to(self.jack_client.get_ports(is_midi=True, is_input=True))
		self.active_value()
		pass
