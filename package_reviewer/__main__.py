import argparse
from pathlib import Path

from .base import CheckRunner
from .checks import all_checkers


def main():
    parser = argparse.ArgumentParser(description="Check a Sublime Text package for common errors.")
    parser.add_argument("path", type=Path,
                        help="Path to the package to be checked.")
    args = parser.parse_args()

    runner = CheckRunner(all_checkers)
    runner.run(args.path)


if __name__ == '__main__':
    main()
