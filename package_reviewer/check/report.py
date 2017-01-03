from collections import namedtuple
import traceback


class Report(namedtuple("_Report", "message context exception exc_info")):
    __slots__ = ()

    _indent = " " * 4

    def report(self):
        print("- {}".format(self.message))
        for elem in self.details:
            print("{}{}".format(self._indent, elem))
        if self.exc_info:
            traceback.print_exception(*self.exc_info)

    @property
    def details(self):
        details = []
        for cont in self.context:
            details.append("{}".format(cont))
        if self.exception:
            details.append("Exception: {}".format(self.exception))
        return tuple(details)
