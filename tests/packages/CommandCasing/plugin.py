from sublime_plugin import ApplicationCommand

# The print calls show what sublime_plugin.Command.name
# translates the class names to.


class not_pascal_case_command(ApplicationCommand):

    def run(self):
        print("not_pascal_case")


class not_PascalCaseCommand(ApplicationCommand):

    def run(self):
        print("not__pascal_case")


class not_PASCALcase_command(ApplicationCommand):

    def run(self):
        print("not__pASCALcase")


class NotPascalCase_command(ApplicationCommand):

    def run(self):
        print("not_pascal_case")


class NotPASCALCaseCommand(ApplicationCommand):

    def run(self):
        print("not_pASCALCase")


class PascalCaseCommand(ApplicationCommand):

    def run(self):
        print("pascal_case")
