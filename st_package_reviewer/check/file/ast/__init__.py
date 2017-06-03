import functools
import ast
from pathlib import Path
from st_package_reviewer.check.file import FileChecker
from st_package_reviewer.check import find_all

__all__ = ('AstChecker', 'get_checkers')


class AstChecker(FileChecker, ast.NodeVisitor):
    """Groups checks for python source code."""

    def __init__(self, base_path):
        super().__init__(base_path)

    def visit_all_pyfiles(self):
        pyfiles = self.glob("**/*.py")
        for self.current_file in pyfiles:
            with self.current_file.open("r") as f:
                try:
                    root = ast.parse(f.read(), self.current_file)
                except SyntaxError as e:
                    with self.file_context(self.current_file):
                        self.fail("Syntax error at line {}, column {}.".format(e.lineno, e.offset))
                    continue
            self.visit(root)


get_checkers = functools.partial(
    find_all,
    Path(__file__).parent,
    __package__,
    base_class=AstChecker
)
