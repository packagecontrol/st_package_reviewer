import functools
import itertools
import json
import logging
import plistlib
import xml.etree.ElementTree as ET

from ..base import Checker
from .. import jsonc

l = logging.getLogger(__name__)


class CheckResourceFiles(Checker):

    # Cache results of glob calls
    @functools.lru_cache()
    def glob(self, pattern):
        return list(self.base_path.glob(pattern))

    def globs(self, *patterns):
        return itertools.chain(*(self.glob(ptrn) for ptrn in patterns))

    def check(self):
        for name in dir(self):
            if name.startswith("check_"):
                getattr(self, name)()
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

    def check_jsonc_files(self):
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
                              .format(self._rel_path(file_path)),
                              exception=e)

    def check_plist_files(self):
        plist_file_globs = {
            "**/*.tmLanguage",
            "**/*.tmPreferences",
            "**/*.tmSnippet",
            "**/*.tmTheme",
        }

        for file_path in self.globs(*plist_file_globs):
            with file_path.open() as f:
                try:
                    plistlib.load(f)
                except Exception as e:
                    self.fail("File '{}' is a badly formatted Plist"
                              .format(self._rel_path(file_path)),
                              exception=e)

    def check_xml_files(self):
        for file_path in self.glob("**/*.sublime-snippet"):
            try:
                ET.parse(str(file_path))
            except ET.ParseError as e:
                self.fail("File '{}' is badly formatted XML"
                          .format(self._rel_path(file_path)),
                          exception=e)

    def _rel_path(self, path):
        return path.relative_to(self.base_path)
