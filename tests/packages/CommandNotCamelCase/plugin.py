from sublime_plugin import ApplicationCommand


class not_camel_case_command(ApplicationCommand):

    def run(self):
        print("not_camel_case")


class not_CamelCaseCommand(ApplicationCommand):
    
    def run(self):
        print("not_CamelCaseCommand")


class not_CAMELcase_command(ApplicationCommand):
    
    def run(self):
        print("not_CAMELcase_command")


class NotCamelCase_command(ApplicationCommand):
    
    def run(self):
        print("NotCamelCase_command")


# Maybe this should pass: A name like HTTPDownloadCommand is now not considered CamelCase.
class NotCAMELCaseCommand(ApplicationCommand):
    
    def run(self):
        print("CAMELCaseCommand")


class CamelCaseCommand(ApplicationCommand):
    
    def run(self):
        print("CamelCaseCommand")
