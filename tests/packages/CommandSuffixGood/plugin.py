import sublime_plugin


class AwesomeFooCommand(sublime_plugin.ApplicationCommand):
	
	def run(self):
		print("AwesomeFooCommand")
