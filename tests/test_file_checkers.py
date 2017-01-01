from collections import namedtuple
import logging
from pathlib import Path

import pytest

from package_reviewer.runner import CheckRunner
from package_reviewer.check import file as file_c


def _collect_test_packages():
    this_dir = Path(__file__).with_name("packages")
    for package_path in this_dir.iterdir():
        if not package_path.is_dir():
            continue
        yield package_path


test_packages = list(_collect_test_packages())


@pytest.fixture(scope='function', params=test_packages)
def package_path(request):
    """Path to a package to be tested."""
    return request.param


@pytest.fixture(scope='function')
def check_runner():
    """Return an initialized CheckRunner with all file checkers."""
    checkers = file_c.get_checkers()
    return CheckRunner(checkers)


def config_logging():
    # Ensure we see debug output if tests fail
    logger = logging.getLogger("package_reviewer")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)


config_logging()

# import after logging is configured


##############################################################################


CheckAssert = namedtuple("CheckAssert", "message details")


def _read_check_asserts(file_path):
    """Read CheckAsserts from file."""
    asserts = set()
    if file_path.is_file():
        with file_path.open('r') as f:
            message = None
            details = []
            line_iter = iter(f)

            line = next(line_iter)
            while line:
                assert line.startswith('- ')
                message = line[2:].strip()
                details = []

                for line in line_iter:
                    if not line.startswith(' '):
                        break
                    details.append(line.strip())
                else:
                    line = None

                asserts.add(CheckAssert(message, tuple(details)))

    return asserts


def test_reviewer_integration(package_path, check_runner):
    """Run checks over a package and check if specified failures or warnings were emitted.

    Test packages can specify the minimum required failures (or warnings)
    in files named "failures" and "warnings" respectively.
    If all failures or warnings should be compared,
    specify them in "all_failures" and "all_warnings".
    """

    # Run checks first and report them to stdout,
    # so we have something to inspect when the test fails.
    check_runner.run(package_path)
    check_runner.report()

    failure_asserts = _read_check_asserts(Path(package_path, "failures"))
    all_failure_asserts = _read_check_asserts(Path(package_path, "all_failures"))
    assert not (failure_asserts and all_failure_asserts), \
        "Only one failures meta file is allowed"

    warning_asserts = _read_check_asserts(Path(package_path, "warnings"))
    all_warning_asserts = _read_check_asserts(Path(package_path, "all_warnings"))
    assert not (warning_asserts and all_warning_asserts), \
        "Only one warnings meta file is allowed"

    assert_none = not (failure_asserts or all_failure_asserts
                       or warning_asserts or all_warning_asserts)

    failures = {CheckAssert(failure.message, failure.to_details())
                for failure in check_runner.failures}
    assert len(failures) == len(check_runner.failures), "TODO: Revisit tests"
    warnings = {CheckAssert(warning.message, warning.to_details())
                for warning in check_runner.warnings}
    assert len(warnings) == len(check_runner.warnings), "TODO: Revisit tests"

    assert assert_none or (failures or warnings), \
        "No asserts found for package but there were reports"

    if all_failure_asserts or assert_none:
        assert failures == all_failure_asserts
    elif failures:
        assert failures >= failure_asserts

    if all_warning_asserts or assert_none:
        assert warnings == all_warning_asserts
    elif warnings:
        assert warnings >= warning_asserts
