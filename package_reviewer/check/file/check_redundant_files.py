import logging

from . import FileChecker

l = logging.getLogger(__name__)


class CheckPackageMetadata(FileChecker):

    def check(self):
        if self.sub_path("package-metadata.json").is_file():
            self.fail("'package-metadata.json' is supposed to be automatically generated "
                      "by Package Control during installation")


class CheckPycFiles(FileChecker):

    def check(self):
        pyc_files = self.glob("**/*.pyc")
        if not pyc_files:
            return

        for path in pyc_files:
            if path.with_suffix(".py").is_file():
                self.fail("'{}' is redundant because its corresponding .py file exists"
                          .format(self.rel_path(path)))
