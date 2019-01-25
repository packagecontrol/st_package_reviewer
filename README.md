# st_package_reviewer

[![Build Status](https://travis-ci.org/packagecontrol/st_package_reviewer.svg?branch=master)](https://travis-ci.org/packagecontrol/st_package_reviewer)
[![Coverage Status](https://coveralls.io/repos/github/packagecontrol/st_package_reviewer/badge.svg?branch=master)](https://coveralls.io/github/packagecontrol/st_package_reviewer?branch=master)
[![PyPI](https://img.shields.io/pypi/v/st-package-reviewer.svg)](https://pypi.python.org/pypi/st-package-reviewer)
[![Python Versions](https://img.shields.io/pypi/pyversions/st-package-reviewer.svg)](https://pypi.python.org/pypi/st-package-reviewer)

A tool to review packages for [Sublime Text 3][]
(and its package manager [Package Control][]).
Supports passing local file paths
or URLs to GitHub repositories.

This README focuses on installation and usage of the tool.
For how to *resolve* failures or warnings
reported by the tool,
[refer to the wiki][wiki].


## Installation

Requires **Python 3.4** or higher.

```bash
$ pip install st-package-reviewer
```


## Usage

```
usage: st_package_reviewer [-h] [--version] [--clip] [--repo-only] [-w] [-v]
                           [--debug]
                           [path_or_URL [path_or_URL ...]]

Check a Sublime Text package for common errors.

positional arguments:
  path_or_URL           URL to the repository or path to the package to be checked. If not provided, runs in interactive mode.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --clip                Copy report to clipboard.
  --repo-only           Do not check the package itself and only its repository.
  -w, --fail-on-warnings
                        Return a non-zero exit code for warnings as well.
  -v, --verbose         Increase verbosity.
  --debug               Enter pdb on exceptions. Implies --verbose.

Return values:
    0: No errors
    -1: Invalid command line arguments

Additional return values in non-interactive mode (a combination of bit flags):
    1: Package check finished with failures
    2: Repository check finished with failures
    4: Unable to download repository

Interactive mode:
    Enter package paths or repository URLS continuously.
    Type `c` to copy the last report to your clipboard.
```


[Sublime Text 3]: https://sublimetext.com/
[Package Control]: https://packagecontrol.io/
[wiki]: https://github.com/packagecontrol/st_package_reviewer/wiki
