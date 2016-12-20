from pathlib import Path
import importlib
import logging

from ..base import Checker


__all__ = ('find_all_checkers')

l = logging.getLogger(__name__)


def find_all_checkers():
    """Find and collect all checker subclasses in this package."""
    this_file = Path(__file__)
    all_checkers = set()

    l.info("Collecting checker modules...")
    for checker_file in this_file.parent.glob("*.py"):
        if checker_file == this_file:
            continue

        l.debug("loading %r", checker_file.name)
        module = importlib.import_module(".{}".format(checker_file.stem), __package__)

        for thing in module.__dict__.values():
            if not isinstance(thing, type):  # not a class
                continue

            # l.debug("checking %r", thing)
            if thing is not Checker and issubclass(thing, Checker):
                l.debug("Found Checker subclass %r", thing)
                all_checkers.add(thing)

    l.info("Loaded %d checker modules", len(all_checkers))

    return all_checkers
