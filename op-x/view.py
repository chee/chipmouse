from .screen import Screen
from .controls import Controls

class View():
        name = "abstract view"
        def start(self, screen: Screen, controls: Controls):
                raise Exception("not implemented")
