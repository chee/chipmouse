# TODO
# we need a menu system, based on pillow, writing out to the st7889
# the code below will go under the adl/opn menu, which will also launch adlrt

import argparse
from .mode import Mode

parser = argparse.ArgumentParser()

parser.add_argument("-m", "--mode", type=Mode, choices=Mode, required=True)

args = parser.parse_args()

from .menu import MainMenu

menu = MainMenu(args.mode, [])

menu.show()

if args.mode is Mode.COMPUTER:
	from . import tkroot
	tkroot.mainloop()
if args.mode is Mode.PI:
	import signal
	signal.pause()
