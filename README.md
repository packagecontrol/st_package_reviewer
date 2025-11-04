# st_package_reviewer

[![Build Status](https://travis-ci.org/packagecontrol/st_package_reviewer.svg?branch=master)](https://travis-ci.org/packagecontrol/st_package_reviewer)
[![Coverage Status](https://coveralls.io/repos/github/packagecontrol/st_package_reviewer/badge.svg?branch=master)](https://coveralls.io/github/packagecontrol/st_package_reviewer?branch=master)
[![PyPI](https://img.shields.io/pypi/v/st-package-reviewer.svg)](https://pypi.python.org/pypi/st-package-reviewer)
[![Python Versions](https://img.shields.io/pypi/pyversions/st-package-reviewer.svg)](https://pypi.python.org/pypi/st-package-reviewer)

A tool to review packages for [Sublime Text][]
(and its package manager [Package Control][]).
Supports passing local file paths
or URLs to GitHub repositories.

This README focuses on installation and usage of the tool.
For how to *resolve* failures or warnings
reported by the tool,
[refer to the wiki][wiki].


## Usage as a GitHub Action

See gh_action/README.md for how to run this as a composite action that runs on channel/registry PRs.


## Installation

Requires **Python 3.13**.

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


## Development (uv, Python 3.13)

This repo uses [uv](https://github.com/astral-sh/uv) and targets Python 3.13.

- Setup environment: `uv sync --group dev`
- Run the CLI: `uv run st_package_reviewer --version`
- Run tests: `uv run pytest`
- Lint: `uv run flake8 .`
- Optional watch mode (loop on fail): `uv run pytest -f`
- Optional parallel runs: `uv run pytest -n auto`


[Sublime Text]: https://sublimetext.com/
[Package Control]: https://packagecontrol.io/
[wiki]: https://github.com/packagecontrol/st_package_reviewer/wiki

## Development Workflow

- Tests
  - Quick run: `uv run pytest -q`
  - With coverage: `uv run pytest --cov st_package_reviewer --cov tests --cov-report term-missing`
  - Watch mode (loop on fail): `uv run pytest -f`
  - Parallel runs: `uv run pytest -n auto`

- Run the CLI during development
  - Are we there?: `uv run st_package_reviewer --version`
  - Interactive: `uv run st_package_reviewer`
  - Local path: `uv run st_package_reviewer /path/to/package`
  - GitHub repo URL: `uv run st_package_reviewer https://github.com/owner/repo`

## Publishing

  - Just create a tag named `vX.Y.Z` (e.g., `v0.4.0`)
  - On tag push, `.github/workflows/release.yml` builds and uploads to PyPI
