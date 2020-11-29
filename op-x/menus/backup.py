from typing import List
from ..menu import Menu, Option, MenuWithSubmenus
from shutil import copytree, copy2
from datetime import datetime

class BackupMenu(Menu):
	name = "backup"
	def show(self):
		self.screen.text("starting backup", color=0xffaa00)
	def day_segment(self, today: datetime):
		hour = today.hour
		if hour in range(0, 4):
			return "tomorrow"
		if hour in range(4, 8):
			return "early"
		if hour in range(8, 12):
			return "breakfast"
		if hour in range(12, 14):
			return "lunch"
		if hour in range(14, 17):
			return "afternoon"
		if hour in range(17, 20):
			return "dinner"
		if hour in range(20, 22):
			return "evening"
		if hour in range(22, 24):
			return "bedtime"
	@property
	def target(self):
		today = datetime.today()
		return today.strftime(f"/tmp/op-2/%y.%m.%d.%H.%M.%S_%A-{self.day_segment(today)}").lower()
	@property
	def op1disk(self):
		return "/tmp/op-1"
	def ignore(self, dirpath: str, filenames: List[str]):
		if dirpath == self.op1disk + "/drum" or dirpath == self.op1disk + "/synth":
			return filter(lambda name : name == "user" or name == "snapshot", filenames)
		else:
			return []
	def copy(self, src, dst):
		self.screen.text(f"copying {src} to {dst}", color=(33, 240, 255))
		copy2(src, dst)
	def start(self):
		try:
			copytree(self.op1disk, self.target, ignore=self.ignore, copy_function=self.copy)
			self.screen.text(f"backed up to: {self.target} :D", color=(0, 255, 255))
		except:
			self.screen.error("backup failed, :(")
