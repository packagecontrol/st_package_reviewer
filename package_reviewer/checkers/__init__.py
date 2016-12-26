from pathlib import Path
import importlib
import logging
import functools

from ..file import FileChecker


__all__ = ('get_file_checkers')

l = logging.getLogger(__name__)


@functools.lru_cache()
def _find_all_checkers(parent_class):
    """Find and collect all checker subclasses in this package."""
    this_file = Path(__file__)
    all_checkers = set()

    l.info("Collecting 'checkers' sub-modules...")
    for checker_file in this_file.parent.glob("*.py"):
        if checker_file == this_file:
            continue

        l.debug("Loading %r...", checker_file.name)
        module = importlib.import_module(".{}".format(checker_file.stem), __package__)

        for thing in module.__dict__.values():
            if not isinstance(thing, type):  # not a class
                continue

            # l.debug("checking %r", thing)
            if thing is not parent_class and issubclass(thing, parent_class):
                l.debug("Found %s subclass: %r", parent_class.__class__.__name__, thing)
                all_checkers.add(thing)

    l.info("Loaded %d checkers", len(all_checkers))

    return all_checkers


get_file_checkers = functools.partial(_find_all_checkers, FileChecker)
