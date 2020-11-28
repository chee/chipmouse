import jack
import readchar

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

from view import View

def AdlView(View):
	name = "adl"
	program = Program()
	client = jack.Client("op-x")
	@client.set_process_callback
	def process(self):
		if self.program.changed:
			print("program changed!", program.value())
			self.port.write_midi_event(0, [0xc0, program.value()])

	def start(self, screen):
		# TODO this probably also needs to start ADLrt
		screen.clear()
		screen.text("ADLplug. press q and w to switch instrument.")

		# i'll be sending ProgramChange here based on button presses
		port = client.midi_outports.register("pg")

		midi_in = client.get_ports(is_midi=True, is_input=True)
		midi_out = client.get_ports(is_midi=True, is_input=False)
		ao = client.get_ports(is_midi=False, is_input=False)
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
			raise RuntimeError("Couldn't find op-1. Is it connected?")

		if adl_in is None:
			raise RuntimeError("Couldn't find ADLrt. Is it running?")

		if adl_out[0] is None or adl_out[1] is None:
			raise RuntimeError("couldn't find adl out. is adlrt running? was looking for ADLrt:outport 0 and ADLrt:outport 1")

		if not speakers:
			raise RuntimeError("No physical playback ports")

		self.port = self.client.midi_outports[0]

		with client:

			try:
				for src, dest in zip(adl_out, speakers):
					client.connect(src, dest)
			except:
				print("error connecting. maybe fine.")
			try:
				client.connect(port, adl_in)
			except:
				print("error connecting. possibly fine.")

			try:
				client.connect(op1_out, adl_in)
			except:
				print("error connecting. probably fine.")

			while True:
				# TODO replace this with a abstracted
				# input thing from the menuing system
				key = readchar.readkey()
				print(repr(key))
				if key == "q" or key == '\x1b[C':
					program.inc()
				if key == "w" or key == '\x1b[D':
					program.dec()
				if key == '\x03':
					exit()
