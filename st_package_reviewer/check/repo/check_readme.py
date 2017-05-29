from . import RepoChecker


class CheckReadme(RepoChecker):

    def check(self):
        readme = self.repo.readme()
        if not readme:
            self.fail("Missing a README file")
