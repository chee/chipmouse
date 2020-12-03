from ..controls import Control
from typing import List
from ..menu import Menu, Option, MenuWithSubmenus
from .halt import HaltMenu

class MainMenu(MenuWithSubmenus):
        name = "main"
        def __init__(self, submenus: List[Menu]):
                super().__init__(submenus)
                self.parent = HaltMenu()
                self.parent.parent = self
