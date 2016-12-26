import functools
import itertools
from pathlib import Path

from .base import Checker


class FileChecker(Checker):
    """Adds utilities for file systems to the Checker class."""

    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path

    # Cache results of glob calls
    @functools.lru_cache()
    def glob(self, pattern):
        return list(self.base_path.glob(pattern))

    def globs(self, *patterns):
        return itertools.chain(*(self.glob(ptrn) for ptrn in patterns))

    def sub_path(self, rel_path):
        return Path(self.base_path, rel_path)
