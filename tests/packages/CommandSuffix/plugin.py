import sublime_plugin


class AwesomeFoo(sublime_plugin.ApplicationCommand):

    def run(self):
        print("AwesomeFoo")


class AwesomeFoo2Command(sublime_plugin.ApplicationCommand):

    def run(self):
        print("AwesomeFoo2Command")
