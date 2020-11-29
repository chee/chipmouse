# TODO
# we need a menu system, based on pillow, writing out to the st7889
# the code below will go under the adl/opn menu, which will also launch adlrt

import argparse
from .controls import Controls
from .screen import Screen
from .mode import Mode

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--mode", type=Mode, choices=Mode, required=True)

args = parser.parse_args()

from .menus.backup import BackupMenu
from .menus.main import MainMenu
from .menus.adl import AdlMenu, OpnMenu
from .menus.speak import SpeakMenu

if args.mode is Mode.COMPUTER:
	from . import tkroot
	def loop():
		return tkroot.mainloop()
else:
	def loop():
		while True:
			pass

controls = Controls(args.mode)
screen = Screen(args.mode)
menu = MainMenu([
	OpnMenu(),
	AdlMenu(),
	BackupMenu(),
	SpeakMenu()
])

menu.set_platform(controls=controls,
		  screen=screen)
menu.take_control()
menu.show()
loop()
