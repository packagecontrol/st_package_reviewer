from pathlib import Path
import importlib

from ..base import Checker

__all__ = ('all_checkers')

this_dir = Path(__file__).parent

# Collect all checker subclasses in this package
all_checkers = set()

for checker_file in this_dir.glob("*.py"):
    module = importlib.import_module(".{}".format(checker_file.stem), __package__)
    for thing in module.__dict__.values():
        if issubclass(thing, Checker) and thing is not Checker:
            all_checkers.add(thing)
