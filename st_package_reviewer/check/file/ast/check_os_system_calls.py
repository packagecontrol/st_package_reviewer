from . import AstChecker


class CheckOsSytemCalls(AstChecker):
    """Checks for any calls to os.system and suggests to use subprocess.check_call intead."""

    def check(self):
        self.visit_all_pyfiles()

    def _warn_about_os_system(self, node):
        with self.file_context(self.current_file):
            self.warn("At line {}, column {}, consider replacing os.system with "
                      "subprocess.check_output, or use sublime's Default.exec.ExecCommand. Since "
                      "it is likely that the plugin contains platform-specific code, please make "
                      "sure you thought about the platform key in your pull request."
                      .format(node.lineno, node.col_offset + 1))

    def visit_Call(self, node):
        try:
            attr = node.func.attr
            id = node.func.value.id
        except Exception as e:
            return
        if id == "os" and attr == "system":
            self._warn_about_os_system(node)
