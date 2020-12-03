from PIL import Image, ImageDraw, ImageFont
from .mode import Mode
import textwrap
from .op1_status import Op1Status

class Colors():
	black = (0x00, 0x00, 0x00)
	white = (0xff, 0xff, 0xff)

class Screen():
	current_image = None
	text_height = 24
	margin = 10
	colors = Colors()
	font = ImageFont.load("./op-x/fonts/terx24n.pil")
	def __init__(self, mode):
		self.op1 = Op1Status()
		self.op1.start(error=self.error)
		self.mode = mode
		if mode is Mode.PI:
			from ST7789 import ST7789, BG_SPI_CS_FRONT
			self.st7789 = ST7789(
				rotation=90,
				port=0,
				cs=1,
				dc=9,
				backlight=13,
				spi_speed_hz=80 * 1000 * 1000
			)
			self.width = self.st7789.width
			self.height = self.st7789.height
			self.st7789.begin()
		if mode is Mode.COMPUTER:
			self.width = 240
			self.height = 240
			from . import tkroot
			import tkinter
			from tkinter.constants import TOP
			self.canvas = tkinter.Canvas(tkroot, width=self.width, height=self.height)
			self.canvas.pack()
	def show(self, image: Image.Image, hint=False):
		if not hint:
			self.current_image = image
		if self.op1.connected:
			   ImageDraw.Draw(image).ellipse((220, 220, 230, 230), fill=(0, 255, 0))
		else:
			   ImageDraw.Draw(image).ellipse((220, 220, 230, 230), fill=(255, 0, 0))
		if self.mode is Mode.COMPUTER:
			from tkinter import NW
			from PIL import ImageTk
			self.tkimage = ImageTk.PhotoImage(image)
			self._image = self.canvas.create_image(0, 0, anchor=NW, image=self.tkimage)
			from tkinter.constants import TOP
			self.canvas.pack(side=TOP, expand=True)
		if self.mode is Mode.PI:
			self.st7789.display(image)
	def file(self, name):
		image = Image.open(f"./op-x/images/{name}")
		self.show(image)
	def overlay_text(self, text):
		image = self.current_image.copy()
		ImageDraw.Draw(image).text(xy=(0, self.height - self.text_height),
					   text=text,
					   font=self.font,
					   fill=(100, 200, 250))
		self.show(image, hint=True)
	def overlay_menu_hint(self):
		image = self.current_image.copy()
		width = self.margin / 2
		length = self.margin * 2
		tl_position = ((0, 0), (width, length))
		tr_position = ((self.width, 0), (self.width - width, length))
		bl_position = ((0, self.height - length), (width, self.height))
		ImageDraw.Draw(image).rectangle(xy=tr_position, fill=(255, 150, 0))
		ImageDraw.Draw(image).rectangle(xy=tl_position, fill=(0, 255, 50))
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
					   font=self.font,
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
				ImageDraw.Draw(image).rectangle(
					(
						(0, y),
						(self.width, y + self.text_height)
					),
					self.colors.white)
			ImageDraw.Draw(image).text(xy=xy,
						   text=option,
						   font=self.font,
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
