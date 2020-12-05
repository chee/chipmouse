# TODO
# we need a menu system, based on pillow, writing out to the st7889
# the code below will go under the adl/opn menu, which will also launch adlrt

import argparse
from .system import System
from .controls import Controls
from .screen import Screen
from .mode import Mode
import signal

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--mode",
		    type=Mode,
		    choices=Mode,
		    required=True)

args = parser.parse_args()

from .menus.backup import BackupMenu
from .menus.main import MainMenu
from .menus.adl import AdlMenu, OpnMenu
from .menus.speak import SpeakMenu
from .menus.synth import SynthMenu
from .menus.thru import ThruMenu
from .menus.beat import BeatMenu
from .menus.cc import CcMenu

if args.mode is Mode.COMPUTER:
	from . import tkroot
	def loop():
		return tkroot.mainloop()
else:
	def loop():
		while True:
			signal.pause()

controls = Controls(args.mode)
screen = Screen(args.mode)
system = System(args.mode, screen=screen)
menu = MainMenu([
	CcMenu(),
	SynthMenu(),
	OpnMenu(),
	AdlMenu(),
	ThruMenu(),
	BackupMenu(),
	SpeakMenu(),
	BeatMenu()
])

menu.set_platform(controls=controls,
		  screen=screen,
		  system=system)
menu.take_control()
menu.show()
loop()
