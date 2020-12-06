from eventemitter import EventEmitter

class Settings(EventEmitter):
	bpm = 120
	honk1 = 0
	honk2 = 0
	honk3 = 0
	def set_bpm(self, val):
		self.bpm = val
		self.emit("bpm")
	def set_honk1(self, val):
		self.honk1 = val
		self.emit("honk1")
	def set_honk2(self, val):
		self.honk2 = val
		self.emit("honk2")
	def set_honk3(self, val):
		self.honk3 = val
		self.emit("honk3")

settings = Settings()
