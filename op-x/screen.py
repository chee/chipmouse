from tkinter.constants import TOP
from PIL import Image, ImageDraw
from .mode import Mode
import textwrap

class Colors():
	black = (0x00, 0x00, 0x00)
	white = (0xff, 0xff, 0xff)

class Screen():
	current_image = None
	text_height = 10
	margin = 10
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
			self.width = 240
			self.height = 240
			from . import tkroot
			import tkinter
			self.canvas = tkinter.Canvas(tkroot, width=self.width, height=self.height)
			self.canvas.pack()
	def show(self, image: Image.Image, hint=False):
		if not hint:
			self.current_image = image
		if self.mode is Mode.COMPUTER:
			from tkinter import NW
			from PIL import ImageTk
			self.tkimage = ImageTk.PhotoImage(image)
			self._image = self.canvas.create_image(0, 0, anchor=NW, image=self.tkimage)
			self.canvas.pack(side=TOP, expand=True)
		if self.mode is Mode.PI:
			self.st7789.display(image)
	def overlay_menu_hint(self):
		image = self.current_image.copy()
		width = self.margin / 2
		length = self.margin * 2
		tl_position = ((0, 0), (width, length))
		tr_position = ((self.width, 0), (self.width - width, length))
		bl_position = ((0, self.height - length), (width, self.height))
		ImageDraw.Draw(image).rectangle(xy=tl_position, fill=(255, 150, 0))
		ImageDraw.Draw(image).rectangle(xy=tr_position, fill=(0, 255, 50))
		ImageDraw.Draw(image).rectangle(xy=bl_position, fill=(0, 255, 255))
		self.show(image, hint=True)
	def remove_menu_hint(self):
		if self.current_image:
			self.show(self.current_image)
		else:
			raise RuntimeError("Somehow there was no current_image when trying to remove menu hint?")
	def image(self, color=(0x00, 0x00, 0x00)):
		return Image.new(mode="RGB",
				 size=(self.width, self.height),
				 color=color)
	def clear(self):
		return self.show(self.image())

	def text(self, text, xy=(margin, 0), color=(0xff, 0xff, 0xff)):
		image = self.image()
		wrapped_text = "\n".join(textwrap.wrap(text, width=self.width // 6))
		ImageDraw.Draw(image).text(xy=xy,
					   text=wrapped_text,
					   fill=color)
		return self.show(image)
	def error(self, text):
		return self.text(text, color=(255, 0, 0))
	def menu(self, options, active):
		image = self.image()
		index = 0
		for option in options:
			y = index * self.text_height
			xy = (self.margin, y)
			color = self.colors.white
			if option == active:
				color = self.colors.black
				ImageDraw.Draw(image).rectangle(((0, y), (self.width, y + self.text_height)), self.colors.white)
			ImageDraw.Draw(image).text(xy=xy,
						   text=option,
						   fill=color)
			index += 1
		return self.show(image)

	def value_menu(self, values, active):
		image = self.image()
		index = 0
		for value in values:
			option = value.name
			# value is 0 to 100
			value_width = value.value * self.width // 100
			y = index * self.text_height
			xy = (self.margin, y)
			text_color = self.colors.white
			if option == active:
				text_color = self.colors.black
				ImageDraw.Draw(image).rectangle(((0, y), (self.width, y + self.text_height)), self.colors.white)
			ImageDraw.Draw(image).rectangle(
				((0, y), (value_width, y + self.text_height)),
				value.color
			)
			ImageDraw.Draw(image).text(xy=xy,
						   text=option,
						   fill=text_color)
			index += 1

		return self.show(image)
