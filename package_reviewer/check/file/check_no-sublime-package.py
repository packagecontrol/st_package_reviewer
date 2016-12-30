from . import FileChecker


class CheckMessages(FileChecker):

    def check(self):
        exists = self.sub_path(".no-sublime-package").is_file()
        if not exists:
            return

        potential_invokers = self.globs("*.py", "**/*.sublime-build")
        if next(potential_invokers, None) is None:
            self.fail("'.no-sublime-package' is defined, "
                      "but no other resource file can make use of it")
        else:
            self.warn("'.no-sublime-package' is defined. "
                      "Please verify that it is *really* necessary")
