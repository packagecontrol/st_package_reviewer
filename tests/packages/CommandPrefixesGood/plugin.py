import sublime_plugin


class AwesomeFooCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print("foo")


class AwesomeBarCommand(sublime_plugin.WindowCommand):

    def run(self):
        print("bar")


class AwesomeBazCommand(sublime_plugin.ApplicationCommand):
    
    def run(self):
        print("baz")
