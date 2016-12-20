import argparse
import logging
from pathlib import Path

from .base import CheckRunner
from .checkers import find_all_checkers


def main():
    parser = argparse.ArgumentParser(description="Check a Sublime Text package for common errors.")
    parser.add_argument("path", type=Path,
                        help="Path to the package to be checked.")
    parser.add_argument("-v", action='store_true', help="Increase verbosity")
    args = parser.parse_args()

    # configure logging
    logger = logging.getLogger("package_reviewer")
    logger.addHandler(logging.StreamHandler())
    log_level = logging.DEBUG if args.v else logging.INFO
    logger.setLevel(log_level)

    # do stuff
    checkers = find_all_checkers()
    runner = CheckRunner(checkers)
    runner.run(args.path)
    runner.report()


if __name__ == '__main__':
    main()
