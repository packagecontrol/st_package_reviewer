import abc
from collections import namedtuple
from contextlib import contextmanager
import functools
import logging
import traceback
import sys

l = logging.getLogger(__name__)


class Report(namedtuple("_Report", "message context exception exc_info")):
    __slots__ = ()

    _indent = " " * 4

    def report(self):
        print("- {}".format(self.message))
        for cont in self.context:
            print("{}{}".format(self._indent, cont))
        if self.exception:
            print("{}Exception: {}".format(self._indent, self.exception))
        if self.exc_info:
            traceback.print_exception(*self.exc_info)


class Checker(metaclass=abc.ABCMeta):

    def __init__(self):
        self.failures = []
        self.warnings = []
        self._checked = False
        self._context_stack = []

        # construct reporting functions
        self.fail = functools.partial(self._append_report, self.failures)
        self.warn = functools.partial(self._append_report, self.warnings)

    def _append_report(self, append_to, message, context=None, exception=None, exc_info=None):
        # TODO capture calling frame
        if context is None:
            context = tuple(self._context_stack)
        report = Report(message, context[:], exception, exc_info)
        append_to.append(report)

    def perform_check(self):
        try:
            self.check()
        except Exception as e:
            msg = "Unhandled exception in 'check' routine"
            self.fail(msg, exception=e, exc_info=sys.exc_info())
            l.exception(msg)
        self._checked = True

    def result(self):
        """Return whether checks ran without issues (`True`) or there were failures (`False`)."""
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")
        return not bool(self.failures)

    def _report(self):
        # This is a very basic report procedure and only for debugging
        if not self._checked:
            raise RuntimeError("Check has not been perfomed yet")

        import pprint
        if self.warnings:
            pprint.pprint(self.warnings)
        if self.failures:
            pprint.pprint(self.failures)

        return self.result()

    @abc.abstractmethod
    def check(self):
        pass

    @contextmanager
    def context(self, context_entry):
        self._context_stack.append(context_entry)
        yield
        assert self._context_stack.pop() == context_entry


class MultiCheckerMixin:

    """Use this mixin class when you want to implement multiple "seaprate" checks."""

    def check(self):
        count = 0
        for name in dir(self):
            if name.startswith("check_"):
                count += 1
                getattr(self, name)()
        if not count:
            raise NotImplementedError("Must implement at least one method starting with `check_`")


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
