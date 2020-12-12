from subprocess import PIPE
from typing import Optional
import jack
import subprocess
from time import sleep
from .jack_client import JackClient
from enum import Enum

class AdlType(Enum):
	adl = 'adl'
	opn = 'opn'

class AdlProcess(JackClient):
	jack_client_name = "chipmouse.sega"
	outport: Optional[jack.OwnMidiPort] = None
	def __init__(self, type=AdlType.adl):
		self.type = type
		command = ["adlrt", "-A", "jack", "-M", "jack"]
		if type is AdlType.adl:
			self.command = command + ["-p", "ADLMIDI"]
		elif type is AdlType.opn:
			self.command = command + ["-p", "OPNMIDI", "-e", "2"]
		else:
			self.command = command

	def write_midi(self, event):
		return self.outport.write_midi_event(0, event)
	def start(self, error):
		self.process = subprocess.Popen(self.command, stdout=PIPE)
		sleep(3)
		self.register_jack_client(midi_out=["program-change"])
		self.outport = self.midi_out[0]
		adl_in = [port for port in
			  self.jack_client.get_ports(
				  is_midi=True,
				  is_input=True)
			  if "ADLrt" in port.name]
		adl_out = [port for port in
			  self.jack_client.get_ports(
				  is_audio=True,
				  is_output=True)
			  if "ADLrt" in port.name]

		if len(adl_in) == 0:
			error("Couldn't find ADLrt. Is it running?")

		if adl_out[0] is None or adl_out[1] is None:
			error("couldn't find adl out. is adlrt running? was looking for ADLrt:outport 0 and ADLrt:outport 1")

		self.connect_all_midi_to(adl_in)
		self.connect_speakers_to(adl_out)
	def stop(self):
		self.deactivate_jack_client()
		self.process.terminate()
		self.process.kill()
	def program_change(self, program):
		self.write_midi([
				0xc0,
				program
			])
		pass

	def jack_process_callback(self, frame):
		if self.outport:
			self.outport.clear_buffer()
