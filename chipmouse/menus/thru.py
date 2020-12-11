from typing import Optional
from ..menu import MenuWithSubmenus, Menu
from ..jack_client import JackClient
import jack
import subprocess
from time import sleep

class Thru(JackClient):
	jack_client_name = "chipmouse.pythru"
	pythru_in: Optional[jack.OwnMidiPort] = None
	pythru_out: Optional[jack.OwnMidiPort] = None
	external = False
	def __init__(self):
		try:
			self.process = subprocess.Popen(["jackthru"])
			sleep(1)
		except:
			print("jackthru process failed")
	def start(self, source_name=str, target_name=str):
		self.register_jack_client(midi_in=["in"],
					  midi_out=["out"])
		# if the rust chipmouse.thru is there, then let's use that
		external_thru_in = self.jack_client.get_port_by_name("chipmouse.thru:input")
		external_thru_out = self.jack_client.get_port_by_name("chipmouse.thru:output")
		self.external = external_thru_in and external_thru_out
		self.pythru_in = self.midi_in[0]
		self.pythru_out = self.midi_out[0]
		self.source = self.jack_client.get_port_by_name(source_name)
		self.target = self.jack_client.get_port_by_name(target_name)
		try:
			self.jack_client.connect(self.source, external_thru_in or self.pythru_in)
		except:
			print("error connecting source to thru")
		try:
			self.jack_client.connect(external_thru_out or self.pythru_out, self.target)
		except:
			print("error connecting thru to target")
	def jack_process_callback(self, frame):
		if self.external:
			return
		if self.pythru_in:
			for offset, data in self.pythru_in.incoming_midi_events():
				self.pythru_out.write_midi_event(self.jack_client.last_frame_time + offset, data)
				print("sending {data}")
	def quit(self):
		self.deactivate_jack_client()
		if self.process:
			self.process.terminate()


class Watcher(JackClient):
	jack_client_name = "chipmouse.thruwatcher"
	def start(self):
		self.register_jack_client()
	def jack_process_callback(self, frame):
		pass
	def quit(self):
		self.deactivate_jack_client()

class ConnectedMenu(Menu):
	def __init__(self, name):
		self.name = name
	def start(self, source, target):
		self.target = target
		self.source = source
		# self.process = subprocess.Popen(["jackthru", self.source,
		# self.target])
		self.thru = Thru()
		self.thru.start(source, target)
	def show(self):
		self.screen.text(f"{self.source} is connected to {self.target}",
				 color=(0, 255, 0))
	def quit(self):
		self.thru.quit()
		super().quit()

class TargetMenu(MenuWithSubmenus):
	def __init__(self, name):
		self.name = name
	def start(self, source, targets):
		self.source = source
		self.targets = targets
		super().__init__([ConnectedMenu(target) for target in targets])
	def select(self, option):
		option.value.start(self.source, option.name)
		option.value.show()
		option.value.take_control()

class ThruMenu(MenuWithSubmenus):
	name = "MIDITHRU"
	def __init__(self):
		pass
	def start(self):
		self.watcher = Watcher()
		self.watcher.start()
		sources = [port.name for port in self.watcher.jack_client.get_ports(is_midi=True, is_output=True)]
		self.targets = [port.name for port in self.watcher.jack_client.get_ports(is_midi=True, is_input=True)]
		super().__init__([TargetMenu(source) for source in sources])
		# self.thru = Thru()
		# self.thru.start()
		# self.process = subprocess.Popen(["jackthru", source_name, target_name])
	def quit(self):
		self.watcher.quit()
		super().quit()
	def select(self, option):
		option.value.start(option.name, self.targets)
		option.value.show()
		option.value.take_control()
