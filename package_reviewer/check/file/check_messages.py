import json

from semver import SemVer

from . import FileChecker


class CheckMessages(FileChecker):

    def check(self):
        folder_exists = self.sub_path("messages").is_dir()
        file_exists = self.sub_path("messages.json").is_file()

        if not (folder_exists or file_exists):
            return
        elif folder_exists and not file_exists:
            self.fail("`messages` folder exists, but `messages.json` does not")
            return
        assert file_exists

        with self.sub_path("messages.json").open() as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                self.fail("unable to load `messages.json`", exception=e)
                return

        for key, rel_path in data.items():
            if key == "install":
                pass
            elif SemVer.valid(key):
                pass
            else:
                self.fail("messages.json: Key {!r} is not 'install' or a valid semantic version"
                          .format(key))

            messsage_path = self.sub_path(rel_path)
            if not messsage_path.is_file():
                self.fail("messages.json: File {!r}, as specified by key {!r}, does not exist"
                          .format(rel_path, key))
