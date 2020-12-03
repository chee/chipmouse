from ..controls import Control
from typing import List
from ..menu import Menu, Option, MenuWithSubmenus
from os import system

class MainMenu(MenuWithSubmenus):
        name = "main"
        quit_counter = 0
        def handle_control_up(self, control):
                super().handle_control_up(control)
                if control is not Control.menu_exit:
                        self.quit_counter = 0
        def quit(self):
                super().quit()
                self.quit_counter += 1
                if self.quit_counter == 4:
                        system("sudo halt")
