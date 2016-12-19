import abc
from collections import namedtuple


CFailure = namedtuple("CFailure", "reason details exc_info")
# `Warning` is a built-in
CWarning = namedtuple("CWarning", "description")


class Checker(metaclass=abc.ABCMeta):

    def __init__(self, base_path):
        self.base_path = base_path
        self.failures = []
        self.warnings = []

    def fail(self, reason, details=None, exc_info=None):
        failure = CFailure(reason, details, exc_info)
        self.failures.append(failure)

    def warn(self, description):
        # Warnings don't cause checks to fail
        warning = CWarning(description)
        self.warnings.append(warning)

    def perform_check(self):
        try:
            self.check()
        except Exception as e:
            self.fail("Unhandled exception in 'check' routine", exc_info=e)

    def report(self):
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

    def run(self, *args, **kwargs):
        objs = []
        for checker in self.checkers:
            checker_obj = checker(*args, **kwargs)
            checker_obj.perform_check()
            objs.append(checker_obj)

        # TODO report
