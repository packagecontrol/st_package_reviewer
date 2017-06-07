import sublime_plugin


class FooCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        print("foo")


class BarCommand(sublime_plugin.WindowCommand):

    def run(self):
        print("bar")


class BazCommand(sublime_plugin.ApplicationCommand):
    
    def run(self):
        print("baz")
