from subprocess import PIPE
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
                return self.port.write_midi_event(0, event)
        def start(self, error):
                self.process = subprocess.Popen(self.command, stdout=PIPE)
                sleep(1)
                client = self.client = jack.Client("op-x")
                client.midi_outports.register("pg")
                midi_in = client.get_ports(is_midi=True, is_input=True)
                midi_out = client.get_ports(is_midi=True, is_input=False)
                self.speakers = client.get_ports(is_physical=True, is_input=True)

                self.op1_out = None
                self.adl_in = []

                for port in midi_out:
                        if "OP-1" in port.name:
                                self.op1_out = port
                                break

                for port in midi_in:
                        if "ADLrt" in port.name:
                                self.adl_in.append(port)

                self.adl_out = [
                        client.get_port_by_name("ADLrt:outport 0"),
                        client.get_port_by_name("ADLrt:outport 1")
                ]

                if self.op1_out is None:
                        error("Couldn't find op-1. Is it connected?")

                if len(self.adl_in) == 0:
                        error("Couldn't find ADLrt. Is it running?")

                if self.adl_out[0] is None or self.adl_out[1] is None:
                        error("couldn't find adl out. is adlrt running? was looking for ADLrt:outport 0 and ADLrt:outport 1")

                if not self.speakers:
                        error("No physical playback ports")

                client.set_process_callback(self._jack_process_callback)
                client.activate()

                try:
                        for src, dest in zip(self.adl_out, self.speakers):
                                client.connect(src, dest)
                except:
                        print("error connecting. maybe fine.")
                try:
                        for adl_in in self.adl_in:
                                client.connect(self.port, adl_in)
                except:
                        print("error connecting. possibly fine.")
                try:
                        for adl_in in self.adl_in:
                                client.connect(self.op1_out, adl_in)
                except:
                        print("error connecting. probably fine.")

        def stop(self):
                for adl_in in self.adl_in:
                        try:
                                self.client.disconnect(self.op1_out, adl_in)
                        except:
                                print(f"didn't disconnect {adl_in}")
                self.client.deactivate()
                self.process.terminate()
                self.process.kill()
        def program_change(self, program):
                self.write_midi([
                                0xc0,
                                program
                        ])
                pass

        def _jack_process_callback(self, frame):
                self.frame += frame
