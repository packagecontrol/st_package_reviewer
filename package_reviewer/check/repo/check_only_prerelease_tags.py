from . import RepoChecker


class CheckOnlyPrereleaseTags(RepoChecker):

    def check(self):
        if not self.semver_tags:
            return

        for sem_tag in self.semver_tags:
            if sem_tag.version.prerelease is None:
                break
        else:
            self.warn("Only found pre-release tags.")
