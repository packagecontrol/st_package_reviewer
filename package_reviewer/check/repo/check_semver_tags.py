import re


from . import RepoChecker


class CheckSemverTags(RepoChecker):

    def check(self):
        if not self.semver_tags:
            msg = "No semantic version tags found. See http://semver.org."
            for tag in self.tags:
                if re.search(r"(v|^)\d+\.\d+$", tag.name):
                    msg += " Semantic versions consist of exactly three numeric parts."
                    break
            self.fail(msg)
