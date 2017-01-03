import re

from . import RepoChecker


class CheckSemverTags(RepoChecker):

    def check(self):

        if not self.semver_tags:
            msg = "No semantic version tags found"
            if not self.tags:
                msg += " (no tags found at all)"
            for tag in self.tags:
                if re.search(r"(v|^)\d+\.\d+$", tag.name):
                    msg += " (semantic versions consist of exactly three numeric parts)"
                    break
            self.fail(msg)


class CheckOnlyPrereleaseTags(RepoChecker):

    def check(self):
        if not self.semver_tags:
            return

        for sem_tag in self.semver_tags:
            if sem_tag.version.prerelease is None:
                break
        else:
            self.warn("Only found pre-release tags.")
