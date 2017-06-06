import platform, sublime, sublime_plugin


class AwesomeFooCommand(sublime_plugin.ApplicationCommand):
    
    def run(self):
        if "Darwin" in platform.platform():
            print("Darwin")
        else:
            print("not supported")


class AwesomeBarCommand(sublime_plugin.ApplicationCommand):
    
    def run(self):
        if sublime.platform() == "linux":
            print("linux")
        elif sublime.platform() == "osx":
            print("osx")
        elif sublime.platform() == "windows":
            print("windows")
        else:
            print("unknown: %s" % sublime.platform())
