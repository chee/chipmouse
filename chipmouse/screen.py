from .controls import Level
from PIL import Image, ImageDraw, ImageFont
from .mode import Mode
import textwrap
from .op1_status import op1

class Colors():
	inactive_background = (0x30, 0x30, 0x30)
	inactive_text = (0xff, 0xff, 0xff)
	active_background = (0xff, 0xff, 0x00)
	active_text = (0x00, 0x00, 0x00)

class Screen():
	current_image = None
	text_height = 24
	margin = 10
	colors = Colors()
	font = ImageFont.load("./chipmouse/fonts/terx24b.pil")
	def __init__(self, mode, controls):
		self.controls = controls
		self.op1 = op1
		self.op1.start(error=self.error)
		self.mode = mode
		if mode is Mode.PI:
			from ST7789 import ST7789
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
		if self.controls.Level is Level.menu:
			image = self.create_menu_hint(image)
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
		image = Image.open(f"./chipmouse/images/{name}")
		self.show(image)
	def overlay_text(self, text):
		image = self.current_image.copy()
		ImageDraw.Draw(image).text(xy=(0, self.height - self.text_height),
					   text=text,
					   font=self.font,
					   fill=(100, 200, 250))
		self.show(image, hint=True)
	def create_menu_hint(self, image):
		width = self.margin / 2
		length = self.margin * 2
		tl_position = ((0, 0), (width, length))
		tr_position = ((self.width, 0), (self.width - width, length))
		bl_position = ((0, self.height - length), (width, self.height))
		ImageDraw.Draw(image).rectangle(xy=tr_position, fill=(255, 150, 0))
		ImageDraw.Draw(image).rectangle(xy=tl_position, fill=(30, 255, 50))
		ImageDraw.Draw(image).rectangle(xy=bl_position, fill=(30, 255, 255))
		return image
	def overlay_menu_hint(self):
		# image = self.current_image.copy()
		# self.show(self.create_menu_hint(image), hint=True)
		pass
	def remove_menu_hint(self):
		if self.current_image:
			self.show(self.current_image)
		else:
			raise RuntimeError("Somehow there was no current_image when trying to remove menu hint?")
	def image(self, color=colors.inactive_background):
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
		prev_lines = 0
		for option in options:
			y = (index + prev_lines) * self.text_height
			xy = (self.margin, y)
			color = self.colors.inactive_text
			lines = textwrap.wrap(option, width=20)
			prev_lines = len(lines) - 1
			if option == active:
				color = self.colors.active_text
				ImageDraw.Draw(image).rectangle(
					(
						(0, y),
						(self.width, (y + (len(lines) * self.text_height)))
					),
					self.colors.active_background)
			ImageDraw.Draw(image).text(xy=xy,
						   text="\n".join(lines),
						   font=self.font,
						   fill=color)
			index += 1
		return self.show(image)

	def value_menu(self, values, active):
		image = self.image()
		top = self.text_height
		for index, value in enumerate(values):
			option = value.name
			value_width = value.index * self.width // value.max
			y = top + (index * (self.text_height + 1))
			x = self.margin
			height = (self.text_height + 1)
			text_color = (0x00, 0x00, 0x00)
			if option == active:
				ImageDraw.Draw(image).rectangle(
					((0, y), (self.width, y + height)),
					self.colors.active_background)
			else:
				ImageDraw.Draw(image).rectangle(
					((0, y), (self.width, y + height)),
					(0x99, 0x99, 0x99))
			ImageDraw.Draw(image).rectangle(
				((0, y), (value_width, y + height)),
				value.color
			)

			ImageDraw.Draw(image).text(xy=(x, y),
						   text=option,
						   fill=text_color,
						   font=self.font)

			vtext = str(value.value)
			twidth = len(vtext) * 10
			ImageDraw.Draw(image).text(xy=(self.width - twidth, (y + self.text_height / 2) - 5),
						   text=vtext,
						   fill=text_color)
		ImageDraw.Draw(image).text(xy=(0, 0), text="-", font=self.font)
		ImageDraw.Draw(image).text(xy=(self.width - 14, 0), text="+", font=self.font)
		ImageDraw.Draw(image).text(xy=(0, self.height - 24), text="f", font=self.font)

		return self.show(image)
