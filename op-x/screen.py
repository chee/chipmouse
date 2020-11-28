from tkinter.constants import TOP
from PIL import Image, ImageDraw
from .mode import Mode

class Colors():
	black = (0x00, 0x00, 0x00)
	white = (0xff, 0xff, 0xff)

class Screen():
	current_image = None
	text_height = 10
	colors = Colors()
	def __init__(self, mode):
		self.mode = mode
		if mode is Mode.PI:
			from ST7789 import ST7789
			self.st7789 = ST7789(
				rotation=90,
				port=0,
				cs=1,
				dc=9,
				backlight=13,
				# TODO ???
				spi_speed_hz=80 * 1000 * 1000
			)
			self.width = self.st7789.width
			self.height = self.st7789.height
		if mode is Mode.COMPUTER:
			self.width = 200
			self.height = 200
			from . import tkroot
			import tkinter
			self.canvas = tkinter.Canvas(tkroot, width=self.width, height=self.height)
			self.canvas.pack()
	def show(self, image: Image.Image):
		if self.mode is Mode.COMPUTER:
			from tkinter import NW
			from PIL import ImageTk
			self.tkimage = ImageTk.PhotoImage(image)
			self._image = self.canvas.create_image(0, 0, anchor=NW, image=self.tkimage)
			self.canvas.pack(side=TOP, expand=True)
		if self.mode is Mode.PI:
			self.st7789.display(image)
	def image(self, color=(0x00, 0x00, 0x00)):
		return Image.new(mode="RGB",
				 size=(self.width, self.height),
				 color=color)
	def clear(self):
		print("clear")
		return self.show(self.image())

	def text(self, text, xy=(0, 0), color=(0xff, 0xff, 0xff)):
		print("text:", text)
		image = self.image()
		ImageDraw.Draw(image).text(xy=xy,
					   text=text,
					   fill=color)
		return self.show(image)

	def menu(self, options, active):
		image = self.image()
		index = 0
		for option in options:
			y = index * self.text_height
			print(option)
			xy = (0, y)
			color = self.colors.white
			if option == active:
				color = self.colors.black
				ImageDraw.Draw(image).rectangle((xy, (self.width, y + self.text_height)), self.colors.white)
			ImageDraw.Draw(image).text(xy=xy,
						   text=option,
						   fill=color)
			index += 1

		return self.show(image)
