import sublime
import sublime_plugin

# This may fail
sublime.load_settings()

# This is safe
sublime.arch()


def plugin_loaded():
    # Also safe
    sublime.load_settings()


class Listener(sublime_plugin.EventListener):
    def __init__(self):
        # Again, unsafe
        sublime.run_command()

    def on_load(self, view):
        # Safe again
        sublime.windows()


class SomeCommand(sublime_plugin.WindowCommand):
    def __init__(self):
        # This is safe, though
        sublime.run_command()


def random_func():
    # Generally safe
    sublime.load_resource()


# but not if called from within the global module scope
random_func()
