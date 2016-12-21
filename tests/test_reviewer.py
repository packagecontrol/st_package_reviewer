import logging
from pathlib import Path

import pytest

from package_reviewer.base import CheckRunner
from package_reviewer.checkers import find_all_checkers


def _collect_test_packages():
    this_dir = Path(__file__).with_name("packages")
    for package_path in this_dir.iterdir():
        if not package_path.is_dir():
            continue
        yield package_path


test_packages = list(_collect_test_packages())


@pytest.fixture(scope='function', params=test_packages)
def package_path(request):
    return request.param


@pytest.fixture(scope='function')
def check_runner():
    return CheckRunner(find_all_checkers())


def config_logging():
    # Ensure we see debug output if tests fail
    logger = logging.getLogger("package_reviewer")
    logger.addHandler(logging.StreamHandler())
    log_level = logging.DEBUG
    logger.setLevel(log_level)


config_logging()


##############################################################################


def _read_file_to_set(file_path):
    if file_path.is_file():
        with file_path.open('r') as f:
            lines = {line.strip() for line in f}

        return lines - {""}
    else:
        return set()


def test_reviewer_integration(package_path, check_runner):
    """Run checks over a package and check if specified failures or warnings were emitted.

    Test packages can specify the minimum required failures (or warnings)
    in files named "failures" and "warnings" respectively.
    If all failures or warnings should be compared,
    specify them in "all_failures" and "all_warnings".
    """
    expected_failures = _read_file_to_set(Path(package_path, "failures"))
    all_expected_failures = _read_file_to_set(Path(package_path, "all_failures"))
    assert not (expected_failures and all_expected_failures), \
        "Only one failures meta file is allowed"

    expected_warnings = _read_file_to_set(Path(package_path, "warnings"))
    all_expected_warnings = _read_file_to_set(Path(package_path, "all_warnings"))
    assert not (expected_warnings ^ all_expected_warnings), \
        "Only one warnings meta file is allowed"

    assert (expected_failures or all_expected_failures
            or expected_warnings or all_expected_warnings), \
        "No expected failures or warnings found in package"

    check_runner.run(package_path)

    failures = set(failure.message for failure in check_runner.failures)
    assert failures & expected_failures == expected_failures
    if all_expected_failures:
        assert failures == all_expected_failures

    warnings = set(warning.message for warning in check_runner.warnings)
    assert warnings & expected_warnings == expected_warnings
    if all_expected_warnings:
        assert warnings == all_expected_warnings
