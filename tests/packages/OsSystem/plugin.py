import sublime_plugin, os

class AwesomeFooCommand(sublime_plugin.ApplicationCommand):
    
    def run(self):
        os.system("which ls") # Won't work on windows
