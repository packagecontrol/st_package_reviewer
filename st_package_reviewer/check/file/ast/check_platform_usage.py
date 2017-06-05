from . import AstChecker

class CheckPlatformUsage(AstChecker):
    """Checks wether the plugin uses the platform package and warn about it. Suggests to use 
    sublime.platform() and sublime.arch(). If it uses the platform package and/or 
    sublime.platform(), checks if the commit has a platform key. If not, warn about it."""

    def check(self):
        self.counter = 0
        self.visit_all_pyfiles()
        if self.counter > 0:
            self.warn("Detected platform usage: Make sure you thought about the platform key in "
                "your pull request.")

    def _warn_platform_module_usage(self, node):
        self.counter += 1
        with self.file_context(self.current_file):
            self.warn("At line {}, column {}, consider replacing the platform module by "
                "using sublime.platform() and sublime.arch()".format(node.lineno, node.col_offset))

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
            self.counter += 1

