import json
import plistlib
import xml.etree.ElementTree as ET

from . import FileChecker
import jsonc


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
