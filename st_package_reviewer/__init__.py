"""Review packages for Sublime Text."""

try:
    # Prefer the generated version file written by hatch-vcs during build/sync
    from ._version import __version__  # type: ignore
except Exception:
    # Fallback for editable/dev scenarios before build hook runs
    __version__ = "0+unknown"

_debug = False


def debug_active():
    return _debug


def set_debug(value):
    global _debug
    _debug = value
