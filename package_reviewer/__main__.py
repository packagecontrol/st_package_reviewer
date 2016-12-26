import argparse
import logging
from pathlib import Path
import sys

from .base import CheckRunner
from .checkers import get_file_checkers


def main():
    parser = argparse.ArgumentParser(description="Check a Sublime Text package for common errors.")
    parser.add_argument("path", type=Path,
                        help="Path to the package to be checked.")
    parser.add_argument("-v", action='store_true', help="Increase verbosity")
    args = parser.parse_args()

    # configure logging
    l = logging.getLogger("package_reviewer")
    l.addHandler(logging.StreamHandler())
    log_level = logging.DEBUG if args.v else logging.INFO
    l.setLevel(log_level)

    # verify args
    if not args.path.is_dir():
        l.error("'%s' is not a directory", args.path)
        return -1
    else:
        l.info("Package path: %s", args.path)

    # do stuff
    checkers = get_file_checkers()
    runner = CheckRunner(checkers)
    runner.run(args.path)
    return not runner.report()


if __name__ == '__main__':
    sys.exit(main())
