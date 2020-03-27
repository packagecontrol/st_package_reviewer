"""Review packages for Sublime Text."""

__version__ = "0.4.0-dev"

_debug = False


def debug_active():
    return _debug


def set_debug(value):
    global _debug
    _debug = value
