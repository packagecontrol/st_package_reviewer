import argparse
import logging
from pathlib import Path
import sys

from . import set_debug, debug_active
from .runner import CheckRunner
from .check import file as file_c


def main():
    parser = argparse.ArgumentParser(description="Check a Sublime Text package for common errors.")
    parser.add_argument("path", type=Path,
                        help="Path to the package to be checked.")
    parser.add_argument("--verbose", "-v", action='store_true',
                        help="Increase verbosity.")
    parser.add_argument("--debug", action='store_true',
                        help="Enter pdb on excpetions. Implies --verbose.")
    args = parser.parse_args()

    # post parsing
    if args.debug:
        args.verbose = True
        set_debug(True)

    # configure logging
    l = logging.getLogger("package_reviewer")
    l.addHandler(logging.StreamHandler())
    log_level = logging.DEBUG if args.verbose else logging.INFO
    l.setLevel(log_level)

    # verify args
    if not args.path.is_dir():
        l.error("'%s' is not a directory", args.path)
        return -1
    else:
        l.info("Package path: %s", args.path)

    # collect checkers (after logging is configured)

    # do stuff
    checkers = file_c.get_checkers()
    try:
        runner = CheckRunner(checkers)
        runner.run(args.path)
        return not runner.report()
    except Exception:
        if debug_active():
            import pdb
            pdb.post_mortem()
        raise


if __name__ == '__main__':
    sys.exit(main())
