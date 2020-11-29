import jack
import subprocess
from time import sleep

from enum import Enum

class Program():
	_value = 0x00
	changed = False
	def inc(self):
		self._value += 0x01
		if self._value > 0xff:
			self._value = 0x00
		self.changed = True
	def dec(self):
		self._value -= 0x01
		if self._value < 0x00:
			self._value = 0xff
		self.changed = True

	def value(self):
		self.changed = False
		return self._value

class AdlType(Enum):
	adl = 'adl'
	opn = 'opn'

class AdlProcess():
	frame = 0
	jack_client_name = "op-x"
	def __init__(self, type=AdlType.adl):
		self.type = type
		if type is AdlType.adl:
			self.command = ["adlrt", "-p", "ADLMIDI"]
		elif type is AdlType.opn:
			self.command = ["adlrt", "-p", "OPNMIDI"]
		else:
			self.command = ["adlrt"]

	@property
	def port(self):
		return self.client.midi_outports[0]
	def write_midi(self, event):
		return self.port.write_midi_event(self.frame, event)
	def start(self, error):
		self.process = subprocess.Popen(self.command)
		sleep(1)
		client = self.client = jack.Client("op-x")
		client.midi_outports.register("pg")
		midi_in = client.get_ports(is_midi=True, is_input=True)
		midi_out = client.get_ports(is_midi=True, is_input=False)
		speakers = client.get_ports(is_physical=True, is_input=True)

		op1_out = None
		adl_in = None

		for port in midi_out:
			if "OP-1" in port.name:
				op1_out = port
				break

		for port in midi_in:
			if "ADLrt" in port.name:
				adl_in = port
				break
		adl_out = [
			client.get_port_by_name("ADLrt:outport 0"),
			client.get_port_by_name("ADLrt:outport 1")
		]

		if op1_out is None:
			error("Couldn't find op-1. Is it connected?")

		if adl_in is None:
			error("Couldn't find ADLrt. Is it running?")

		if adl_out[0] is None or adl_out[1] is None:
			error("couldn't find adl out. is adlrt running? was looking for ADLrt:outport 0 and ADLrt:outport 1")

		if not speakers:
			error("No physical playback ports")

		client.set_process_callback(self._jack_process_callback)
		client.activate()

		try:
			for src, dest in zip(adl_out, speakers):
				client.connect(src, dest)
		except:
			print("error connecting. maybe fine.")
		try:
			client.connect(self.port, adl_in)
		except:
			print("error connecting. possibly fine.")
		try:
			client.connect(op1_out, adl_in)
		except:
			print("error connecting. probably fine.")

	def stop(self):
		self.client.deactivate()
		self.process.terminate()
	def program_change(self, program):
		self.write_midi([
				0xc0,
				program
			])
		pass

	def _jack_process_callback(self, frame):
		self.frame += frame
		pass
