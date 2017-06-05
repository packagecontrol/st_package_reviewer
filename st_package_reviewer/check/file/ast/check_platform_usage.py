from . import AstChecker


class CheckPlatformUsage(AstChecker):
    """If the plugin uses the platform package and/or sublime.platform(), issue a warning."""

    def check(self):
        self.visit_all_pyfiles()

    def _warn_platform_module_usage(self, node):
        with self.file_context(self.current_file):
            self.warn("At line {}, column {}, consider replacing the platform module by "
                      "using sublime.platform() and sublime.arch() Since it is likely likely that "
                      "the plugin contains platform-dependent code, please make sure you thought "
                      "about the platform key in your pull request."
                      .format(node.lineno, node.col_offset))

    def _warn_sublime_platform_usage(self, node):
        with self.file_context(self.current_file):
            self.warn("It looks like you're using platform-dependent code at line {}, column {}. "
                      "Please make sure you thought about the platform key in your pull request."
                      .format(node.lineno, node.col_offset))

    def visit_Import(self, node):
        for alias_node in node.names:
            name = alias_node.name
            if name == "platform":
                self._warn_platform_module_usage(node)

    def visit_ImportFrom(self, node):
        if node.module == "platform":
            self._warn_platform_module_usage(node)

    def visit_Call(self, node):
        try:
            attr = node.func.attr
            id = node.func.value.id
        except Exception as e:
            return
        if id == "sublime" and attr in ("platform", "arch"):
            self._warn_sublime_platform_usage(node)
