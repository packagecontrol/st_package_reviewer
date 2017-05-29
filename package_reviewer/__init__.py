"""Review Sublime Text packages.
"""

__version__ = "0.2.1"

_debug = False


def debug_active():
    return _debug


def set_debug(value):
    global _debug
    _debug = value
