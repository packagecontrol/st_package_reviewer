import logging

from . import FileChecker


l = logging.getLogger(__name__)


class CheckPluginsInRoot(FileChecker):

    def check(self):
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


class CheckHasResourceFiles(FileChecker):

    def check(self):
        # Files with a hidden extension are excluded,
        # as they serve no purpose without another file using them
        # (e.g. a plugin).
        resource_file_globs = {
            "*.py",
            "**/*.sublime-build",
            "**/*.sublime-color-scheme",
            # "**/*.hidden-color-scheme",
            "**/*.sublime-commands",
            "**/*.sublime-completions",
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
            # "**/*.hidden-tmTheme",
            # hunspell dictionaries
            "**/*.aff",
            "**/*.dic",
        }

        has_resource_files = any(self.glob(ptrn) for ptrn in resource_file_globs)
        if not has_resource_files:
            self.fail("The package does not define any file that interfaces with Sublime Text")


class CheckHasSublimeSyntax(FileChecker):

    def check(self):
        syntax_files = self.glob("**/*.sublime-syntax")

        for path in syntax_files:
            if (
                not path.with_suffix(".tmLanguage").is_file()
                and not path.with_suffix(".hidden-tmLanguage").is_file()
            ):
                with self.file_context(path):
                    self.warn("'.sublime-syntax' support has been added in build 3092 and there "
                              "is no '.tmLanguage' fallback file")
