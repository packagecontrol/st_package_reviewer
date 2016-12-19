from ..base import Checker


class CheckPluginsInRoot(Checker):

    def check(self):
        plugins_in_root = list(self.base_path.glob("*.py"))
        if plugins_in_root:
            return

        python_files_in_package = list(self.base_path.glob("*/**/*.py"))
        if python_files_in_package:
            self.fail("The package contains {:d} Python files, "
                      "but none of them are in the package root"
                      .format(len(python_files_in_package)))
