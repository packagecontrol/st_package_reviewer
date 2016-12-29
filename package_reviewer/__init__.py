_debug = False


def debug_active():
    return _debug


def set_debug(value):
    global _debug
    _debug = value
