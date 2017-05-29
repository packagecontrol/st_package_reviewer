import functools
import logging
from pathlib import Path

from .. import Checker, find_all
from ... import repo_tools

__all__ = ('RepoChecker', 'get_checkers', )

l = logging.getLogger(__name__)


class RepoChecker(Checker):
    """Groups checks for packages' contents.

    Also adds utilities for file systems to the Checker class.
    """

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    @property
    def tags(self):
        return repo_tools.tags(self.repo)

    @property
    def semver_tags(self):
        return repo_tools.semver_tags(self.repo)


get_checkers = functools.partial(
    find_all,
    Path(__file__).parent,
    __package__,
    base_class=RepoChecker
)
