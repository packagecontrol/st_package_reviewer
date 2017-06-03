import functools
import itertools
from pathlib import Path
import ast

from .. import Checker, find_all

__all__ = ('FileChecker', 'get_checkers')


class FileChecker(Checker, ast.NodeVisitor):
    """Groups checks for packages' contents.

    Also adds utilities for file systems to the Checker class.
    """

    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path

    @staticmethod
    # Cache results of glob calls (this is naive, but realistic)
    @functools.lru_cache()
    def _glob(base_path, pattern):
        return list(base_path.glob(pattern))

    def glob(self, pattern):
        return self._glob(self.base_path, pattern)

    def globs(self, *patterns):
        return itertools.chain(*(self.glob(ptrn) for ptrn in patterns))

    def sub_path(self, rel_path):
        return Path(self.base_path, rel_path)

    def rel_path(self, path):
        return path.relative_to(self.base_path)

    def file_context(self, path):
        try:
            path = self.rel_path(path)
        except ValueError:
            pass
        return self.context("File: {}".format(path))

    def visit_all_pyfiles(self):
        pyfiles = self.glob("**/*.py")
        for self.current_file in pyfiles:
            with open(self.current_file, "r") as f:
                try:
                    root = ast.parse(f.read(), self.current_file)
                except Exception as e:
                    with self.file_context(self.current_file):
                        self.fail("Failed to parse! One possibility is that this is a Python2 "
                            "file with some Python2 constructs no longer valid in Python3.")
                    continue
            self.visit(root)

get_checkers = functools.partial(
    find_all,
    Path(__file__).parent,
    __package__,
    base_class=FileChecker
)
