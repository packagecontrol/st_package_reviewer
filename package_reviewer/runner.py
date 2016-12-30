import logging

l = logging.getLogger(__name__)


class CheckRunner:

    def __init__(self, checkers):
        self.checkers = checkers
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
        return not bool(self.failures)

    def report(self):
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")

        print()
        if self.failures:
            print("Reporting {} failures:".format(len(self.failures)))
        else:
            print("No failures")
        for failure in self.failures:
            failure.report()

        print()
        if self.warnings:
            print("Reporting {} warnings:".format(len(self.warnings)))
        else:
            print("No warnings")

        for warning in self.warnings:
            warning.report()

        return not bool(self.failures)
