from typing import List
from ..menu import Menu, Option
from ..mode import Mode

class MainMenu(Menu):
	name = "main"
	def __init__(self, submenus: List[Menu]):
		options = []
		for menu in submenus:
			menu.parent = self
			options.append(Option(menu.name, menu))
		super().__init__(list(options))
	def select(self, option):
		self.controls.unsubscribe()
		option.value.subscribe()
		return option.value.show()
