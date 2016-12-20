import abc
from collections import namedtuple


CFailure = namedtuple("CFailure", "message details exc_info")
# `Warning` is a built-in
CWarning = namedtuple("CWarning", "message")


class Checker(metaclass=abc.ABCMeta):

    def __init__(self, base_path):
        self.base_path = base_path
        self.failures = set()
        self.warnings = set()
        self._checked = False

    def fail(self, message, details=None, exc_info=None):
        failure = CFailure(message, details, exc_info)
        self.failures.add(failure)

    def warn(self, message):
        # Warnings don't cause checks to fail
        warning = CWarning(message)
        self.warnings.add(warning)

    def perform_check(self):
        try:
            self.check()
        except Exception as e:
            self.fail("Unhandled exception in 'check' routine", exc_info=e)
        self._checked = True

    def result(self):
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")
        return bool(self.failures)

    def report(self):
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")

        # TODO report
        import pprint
        if self.warnings:
            pprint.pprint(self.warnings)
        if self.failures:
            pprint.pprint(self.failures)
            return False
        else:
            return True

    @abc.abstractmethod
    def check(self):
        pass


class CheckRunner:

    def __init__(self, checkers):
        self.checkers = checkers
        self.failures = set()
        self.warnings = set()
        self._checked = False

    def run(self, *args, **kwargs):
        objs = []
        for checker in self.checkers:
            checker_obj = checker(*args, **kwargs)
            objs.append(checker_obj)

            checker_obj.perform_check()
            self.failures |= checker_obj.failures
            self.warnings |= checker_obj.warnings

        self._checked = True

    def report(self):
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")

        print()
        if self.failures:
            print("Reporting {} failures:".format(len(self.failures)))
        else:
            print("No failures")
        for failure in self.failures:
            print(failure)

        print()
        if self.warnings:
            print("Reporting {} warnings:".format(len(self.warnings)))
        else:
            print("No warnings")

        for warning in self.warnings:
            print(warning)

        return bool(self.failures)

