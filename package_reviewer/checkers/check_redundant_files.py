import logging

from ..file import FileChecker

l = logging.getLogger(__name__)


class CheckPackageMetadata(FileChecker):

    def check(self):
        if self.sub_path("package-metadata.json").is_file():
            self.fail("'package-metadata.json' is supposed to be automatically generated "
                      "by Package Control during installation")
