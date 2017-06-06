from sublime_plugin import ApplicationCommand


class not_pascal_case_command(ApplicationCommand):

    def run(self):
        print("not_pascal_case")


class not_PascalCaseCommand(ApplicationCommand):

    def run(self):
        print("not_PascalCaseCommand")


class not_PASCALcase_command(ApplicationCommand):

    def run(self):
        print("not_PASCALcase_command")


class NotPascalCase_command(ApplicationCommand):

    def run(self):
        print("NotPascalCase_command")


# Maybe this should pass:
# A name like HTTPDownloadCommand is translated to "http_download" by ST
class NotPASCALCaseCommand(ApplicationCommand):

    def run(self):
        print("PASCALCaseCommand")


class PascalCaseCommand(ApplicationCommand):

    def run(self):
        print("PascalCaseCommand")
