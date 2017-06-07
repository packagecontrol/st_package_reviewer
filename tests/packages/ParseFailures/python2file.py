import sublime_plugin


class AwesomeFooCommand(sublime_plugin.ApplicationCommand):

	def run(self):
		# Used to be okay in Python2; no longer the case in Python3.
		print "Hello, world!"
