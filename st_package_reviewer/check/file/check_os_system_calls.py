from . import FileChecker
import ast

class CheckOsSytemCalls(FileChecker):
    """Checks for any calls to os.system and suggests to use subprocess.check_call intead."""

    def check(self):
        self.counter = 0
        self.visit_all_pyfiles()
        if self.counter > 0:
            self.warn("Detected os.system usage: Make sure you thought about the platform key in "
                "your pull request.")

    def _warn_about_os_system(self, node):
        self.counter += 1
        with self.file_context(self.current_file):
            self.warn("At line {}, column {}, consider replacing os.system with "
                "subprocess.check_output, or use sublime's Default.exec.ExecCommand.".format(
                    node.lineno, node.col_offset))

    def visit_Call(self, node):
        try:
            attr = node.func.attr
            id = node.func.value.id
        except Exception as e:
            return
        if id == "os" and attr == "system":
            self._warn_about_os_system(node)
