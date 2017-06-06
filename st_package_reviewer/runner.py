import logging
import sys

l = logging.getLogger(__name__)


class CheckRunner:

    def __init__(self, checkers, fail_on_warnings=False):
        self.checkers = checkers
        self.fail_on_warnings = fail_on_warnings
        self.failures = []
        self.warnings = []
        self._checked = False

    def run(self, *args, **kwargs):
        l.debug("\nRunning checkers...")
        objs = []
        for checker in self.checkers:
            checker_obj = checker(*args, **kwargs)
            objs.append(checker_obj)

            checker_obj.perform_check()
            self.failures.extend(checker_obj.failures)
            self.warnings.extend(checker_obj.warnings)
            l.debug("Checker '%s' result: %s",
                    checker_obj.__class__.__name__,
                    checker_obj.result())

        self._checked = True

    def result(self):
        """Return whether checks ran without issues (`True`) or there were failures (`False`)."""
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")
        success = not bool(self.failures)
        if self.fail_on_warnings:
            success &= not bool(self.warnings)
        return success

    def report(self, file=None):
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")
        if file is None:
            file = sys.stdout

        if self.failures:
            print("Reporting {} failures:".format(len(self.failures)), file=file)
        else:
            print("No failures", file=file)
        for failure in self.failures:
            failure.report(file=file)

        print(file=file)  # new line

        if self.warnings:
            print("Reporting {} warnings:".format(len(self.warnings)), file=file)
        else:
            print("No warnings", file=file)

        for warning in self.warnings:
            warning.report(file=file)

        print(file=file)  # new line
