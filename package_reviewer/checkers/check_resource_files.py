import json
import logging
import plistlib
import xml.etree.ElementTree as ET

from ..file import FileChecker
from .. import jsonc

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


class CheckJSONCFiles(FileChecker):

    def check(self):
        # All these files allow comments and trailing commas,
        # which is why we'll call them "jsonc" (JSON with Comments)
        jsonc_file_globs = {
            "**/*.sublime-build",
            "**/*.sublime-commands",
            "**/*.sublime-keymap",
            "**/*.sublime-macro",
            "**/*.sublime-menu",
            "**/*.sublime-mousemap",
            "**/*.sublime-settings",
            "**/*.sublime-theme",
        }

        for file_path in self.globs(*jsonc_file_globs):
            with file_path.open(encoding='utf-8') as f:
                try:
                    jsonc.loads(f.read())
                except json.JSONDecodeError as e:
                    self.fail("File '{}' is badly formatted JSON (with comments)"
                              .format(self.rel_path(file_path)),
                              exception=e)


class CheckPlistFiles(FileChecker):

    def check(self):
        plist_file_globs = {
            "**/*.tmLanguage",
            "**/*.tmPreferences",
            "**/*.tmSnippet",
            "**/*.tmTheme",
        }

        for file_path in self.globs(*plist_file_globs):
            with file_path.open('rb') as f:
                try:
                    plistlib.load(f)
                except ValueError as e:
                    self.fail("File '{}' is a badly formatted Plist"
                              .format(self.rel_path(file_path)),
                              exception=e)


class CheckXmlFiles(FileChecker):

    def check(self):
        for file_path in self.glob("**/*.sublime-snippet"):
            try:
                ET.parse(str(file_path))
            except ET.ParseError as e:
                self.fail("File '{}' is badly formatted XML"
                          .format(self.rel_path(file_path)),
                          exception=e)
