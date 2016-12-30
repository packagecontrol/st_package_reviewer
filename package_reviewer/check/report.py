from collections import namedtuple
import traceback


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
