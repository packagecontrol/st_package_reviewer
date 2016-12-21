import functools
import logging

from ..base import Checker

l = logging.getLogger(__name__)


class CheckResourceFiles(Checker):

    # Cache results of glob calls
    @functools.lru_cache()
    def glob(self, pattern):
        return list(self.base_path.glob(pattern))

    def check(self):
        i = 0
        for name in dir(self):
            if name.startswith("check_"):
                getattr(self, name)()
                i += 1
        assert i == 3, i
        l.debug("CheckResourceFiles.glob cache info: %s", self.glob.cache_info())

    def check_plugins_in_root(self):
        if self.glob("*.py"):
            return

        python_files_in_package = self.glob("*/**/*.py")
        if python_files_in_package:
            l.debug("Non-plugin Python files: %s", python_files_in_package)
            if not self.glob("**/*.sublime-build"):
                self.fail("The package contains {} Python file(s), "
                          "but none of them are in the package root "
                          "and no build system is specified"
                          .format(len(python_files_in_package)))

    def check_has_resource_files(self):
        resource_file_globs = {
            "*.py",
            "**/*.sublime-build",
            "**/*.sublime-commands",
            "**/*.sublime-keymap",
            "**/*.sublime-macro",  # almost useless without other files
            "**/*.sublime-menu",
            "**/*.sublime-mousemap",
            "**/*.sublime-settings",
            "**/*.sublime-snippet",
            "**/*.sublime-syntax",
            "**/*.sublime-theme",
            "**/*.tmLanguage",
            "**/*.tmPreferences",
            "**/*.tmSnippet",
            "**/*.tmTheme",
            # hunspell dictionaries
            "**/*.aff",
            "**/*.dic",
        }

        has_resource_files = any(self.glob(ptrn) for ptrn in resource_file_globs)
        if not has_resource_files:
            self.fail("The package does not define any file that interfaces with Sublime Text")

    # def check_jsonc_files(self):
    #     # All these files allow comments and trailing commas,
    #     # which is why we'll call them "jsonc" (JSON with Comments)
    #     jsonc_file_globs = {
    #         "**/*.sublime-build",
    #         "**/*.sublime-commands",
    #         "**/*.sublime-keymap",
    #         "**/*.sublime-macro",
    #         "**/*.sublime-menu",
    #         "**/*.sublime-mousemap",
    #         "**/*.sublime-settings",
    #         "**/*.sublime-snippet",
    #         "**/*.sublime-syntax",
    #         "**/*.sublime-theme",
    #     }
    #     # TODO
