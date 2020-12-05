from subprocess import PIPE
from typing import Optional
import jack
import subprocess
from time import sleep
from .jack_client import JackClient
import binascii

class Monitor(JackClient):
        jack_client_name = "chipmouse.monitor"
        def __init__(self):
                self.register_jack_client(midi_in=["input"], midi_out=["output"])
                self.input = self.midi_in[0]
                input: jack.OwnMidiPort = self.input
                self.output = self.midi_out[0]
                output: jack.OwnMidiPort = self.output
                input.request_monitor(True)
                output.request_monitor(True)
        def start(self):
                pass
        def stop(self):
                self.deactivate_jack_client()
        def jack_process_callback(self, frame):
                for offset, data in self.input.incoming_midi_events():
                        print(f"input: [{self.jack_client.last_frame_time + offset}] {binascii.hexlify(data).decode()}")
                        self.output.write_midi_event(self.jack_client.last_frame_time + offset, data)
