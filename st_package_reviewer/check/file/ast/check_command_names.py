from . import AstChecker
import re
import ast


class CheckCommandNames(AstChecker):
    """Finds all sublime commands and does various checks on them."""

    def check(self):
        self.prefixes = set()
        self.visit_all_pyfiles()
        if len(self.prefixes) > 1:
            self.warn("Found multiple command prefixes: {}. Consider using one single prefix so as"
                      " to not clutter the command namespace."
                      .format(", ".join(sorted(list(self.prefixes)))))

    # TODO: This only checks immediate base classes; need more traversing for deeper-derived base
    # classes.
    def is_derived_from_command(self, node):
        interesting = ("TextCommand", "WindowCommand", "ApplicationCommand", "ExecCommand")
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                # something of the form module_name.BaseClassName
                if isinstance(base.value, ast.Attribute):
                    if base.value.value.id == "Default":
                        # Something derived from a class in Default... Must be ExecCommand
                        return True
                elif isinstance(base.value, ast.Name):
                    if base.value.id == "sublime_plugin" and base.attr in interesting:
                        return True
            elif isinstance(base, ast.Name):
                # something of the form BaseClassName
                if base.id in interesting:
                    return True
        return False

    def visit_ClassDef(self, node):
        if not self.is_derived_from_command(node):
            return
        # Check if the command is documented.
        docstring = ast.get_docstring(node)
        if not docstring:
            with self.file_context(self.current_file):
                self.warn("At line {}, column {}, the command {} does not have a docstring."
                    .format(node.lineno, node.col_offset, node.name))
        # Check if the command has the "Command" suffix.
        if not node.name.endswith("Command"):
            with self.file_context(self.current_file):
                self.warn("At line {0}, column {1}, consider replacing {2} with "
                          "{2}Command.".format(node.lineno, node.col_offset + 1, node.name))
        # Check if all commands have a common prefix so as to not clutter the command namespace.
        match = re.findall(r"[A-Z][^A-Z]*", node.name)
        if match:
            self.prefixes.add(str(match[0]))
        match = re.match(r"(?x) (^[A-Z][a-z0-9]+[A-Z]$) | (^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)+$) | "
                         "(^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)+[A-Z]$)", node.name)
        if not match:
            with self.file_context(self.current_file):
                self.warn('At line {}, column {}, the command {} is not CamelCase.'.format(
                    node.lineno, node.col_offset + 1, node.name))
