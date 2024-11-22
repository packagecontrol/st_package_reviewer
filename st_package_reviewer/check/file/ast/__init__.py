import functools
import ast
from pathlib import Path
from ....check.file import FileChecker
from ....check import find_all

__all__ = ('AstChecker', 'get_checkers')


class AstChecker(FileChecker, ast.NodeVisitor):
    """Groups checks for python source code."""

    _ast_cache = {}

    def __init__(self, base_path):
        super().__init__(base_path)

    def check(self):
        self.visit_all_pyfiles()

    def visit_all_pyfiles(self):
        pyfiles = self.glob("**/*.py")
        for path in pyfiles:
            with self.file_context(path):
                root = self._get_ast(path)
                if root:
                    self.visit(root)

    def _get_ast(self, path):
        try:
            return self._ast_cache[path]
        except KeyError:
            self._ast_cache[path] = None

        with path.open("r") as f:
            try:
                the_ast = ast.parse(f.read(), path)
            except SyntaxError as e:
                with self.context("Line: {}".format(e.lineno)):
                    self.fail("Unable to parse Python file", exception=e)
            else:
                self._ast_cache[path] = the_ast
                return the_ast

    def node_context(self, node):
        return self.context("Line: {}, Column: {}".format(node.lineno, node.col_offset + 1))


get_checkers = functools.partial(
    find_all,
    Path(__file__).parent,
    __package__,
    base_class=AstChecker
)
