class Printer:
	debugging = False

	@staticmethod
	def debugPrint(self, message):
		if(self.debugging):
			print(message)