import functools
import ast
from pathlib import Path
from st_package_reviewer.check.file import FileChecker
from st_package_reviewer.check import find_all

__all__ = ('AstChecker', 'get_checkers')


class AstChecker(FileChecker, ast.NodeVisitor):
    """Groups checks for python source code."""

    _ast_cache = {}

    def __init__(self, base_path):
        super().__init__(base_path)

    def visit_all_pyfiles(self):
        pyfiles = self.glob("**/*.py")
        for self.current_file in pyfiles:
            root = self._get_ast(self.current_file)
            if root:
                self.visit(root)

    def _get_ast(self, path):
        try:
            return self._ast_cache[path]
        except KeyError:
            self._ast_cache[path] = None

        with path.open("r") as f:
            try:
                # Cast path to string for <py36
                the_ast = ast.parse(f.read(), str(self.current_file))
            except SyntaxError as e:
                with self.file_context(path):
                    self.fail("Unable to parse Python file (column {})".format(e.offset + 1),
                              exception=e)
            else:
                self._ast_cache[path] = the_ast
                return the_ast


get_checkers = functools.partial(
    find_all,
    Path(__file__).parent,
    __package__,
    base_class=AstChecker
)
