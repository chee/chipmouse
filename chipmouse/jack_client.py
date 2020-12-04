from abc import ABCMeta, abstractmethod
from typing import List, Optional
import jack

class JackClient(metaclass=ABCMeta):
	jack_connections = []
	jack_client: Optional[jack.Client] = None

	@property
	@abstractmethod
	def jack_client_name(self) -> str:
		pass

	@abstractmethod
	def jack_process_callback(self, frame):
		pass

	def jack_samplerate_callback(self, samplerate):
		self.samplerate = samplerate

	@property
	def audio_in(self) -> List[jack.OwnPort]:
		return list(self.jack_client.inports)
	@property
	def audio_out(self) -> List[jack.OwnPort]:
		return list(self.jack_client.outports)
	@property
	def midi_in(self) -> List[jack.OwnMidiPort]:
		return list(self.jack_client.midi_inports)
	@property
	def midi_out(self) -> List[jack.OwnMidiPort]:
		return list(self.jack_client.midi_outports)

	def register_jack_client(self, midi_in:List[str]=[], midi_out:List[str]=[], audio_in:List[str]=[], audio_out:List[str]=[]):
		self.jack_client = jack.Client(self.jack_client_name)

		self.jack_connections = []
		for name in midi_in:
			self.jack_client.midi_inports.register(name)
		for name in midi_out:
			self.jack_client.midi_outports.register(name)
		for name in audio_in:
			self.jack_client.inports.register(name)
		for name in audio_out:
			self.jack_client.outports.register(name)
		self.jack_speakers = self.jack_client.get_ports(is_physical=True, is_input=True, is_audio=True)
		self.jack_client.set_samplerate_callback(self.jack_samplerate_callback)
		self.jack_client.set_process_callback(self.jack_process_callback)
		self.jack_client.activate()
	def deactivate_jack_client(self):
		for src, dst in self.jack_connections:
			try:
				self.jack_client.disconnect(src, dst)
			except:
				print(f"didn't disconnect {src} from {dst}")
		self.jack_client.deactivate()
		self.jack_client.close()
		self.jack_client = None
	def connect_all_midi_to(self, ins=[]):
		midi_out = self.jack_client.get_ports(is_midi=True, is_input=False)
		for output in midi_out:
			for input in ins:
				try:
					self.jack_client.connect(output, input)
					self.jack_connections.append([output, input])
				except:
					print(f"error connecting {output} to {input}. probably fine.")
		if len(self.jack_connections) == 0:
			print("warning: didn't connect any midi instruments")
	def connect_speakers_to(self, src=[]):
		if len(src) == 0:
			raise RuntimeError("need at least one source")
		elif len(src) == 1:
			for speaker in self.jack_speakers:
				try:
					self.jack_client.connect(src[0], speaker)
				except:
					print(f"didn't connect {src[0]} to {speaker}")
		elif len(src) == 2:
			for src, dst in zip(src, self.jack_speakers):
				try:
					self.jack_client.connect(src, dst)
				except:
					print(f"didn't connect {src} to {dst}")
		elif len(src) > 2:
			raise RuntimeError(f"too many src ({len(src)}), don't know what you want.")
