from chipmouse.menu import FourValueMenu, MenuColor, MenuValue

class SettingsMenu(FourValueMenu):
	def start(self):
		self.register("bpm",
			      MenuColor.first,
			      range(40, 240),
			      step=10,
			      finestep=1,
			      initial=80,
			      callback=settings.set_bpm)
		self.register("honk1",
			      MenuColor.second,
			      range(1, 128),
			      step=10,
			      finestep=1,
			      initial=47,
			      callback=settings.set_honk1)
		self.register("honk2",
			      MenuColor.third,
			      range(1, 128),
			      step=10,
			      finestep=1,
			      initial=69,
			      callback=settings.set_honk2)
		self.register("honk3",
			      MenuColor.fourth,
			      range(1, 128),
			      step=10,
			      finestep=1,
			      initial=100,
			      callback=settings.set_honk3)
		super().start()

from ..settings import settings
