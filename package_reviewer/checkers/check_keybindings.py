import json
import logging
import re
from pathlib import Path

from .. import jsonc
from ..file import FileChecker


DATA_PATH = Path(__file__).parent.parent / "data"

PLATFORMS = ("Linux", "OSX", "Windows")
PLATFORM_FILENAMES = tuple("Default ({}).sublime-keymap".format(plat)
                           for plat in PLATFORMS)
VALID_FILENAMES = PLATFORM_FILENAMES + ("Default.sublime-keymap",)

l = logging.getLogger(__name__)


class CheckKeybindings(FileChecker):

    def check(self):
        keymap_files = self.glob("**/*.sublime-keymap")

        # ignore unused files
        keymap_files = {path for path in keymap_files
                        if path.name in VALID_FILENAMES}

        if not keymap_files:
            return

        # cache default keymap files
        def_bindings = KeyMapping.default_maps()

        # check for conflicts with default package
        for path in keymap_files:
            platforms = PLATFORMS
            m = re.search(r"\((.*?)\)", path.name)
            if m:
                platforms = {m.group(1)}
            print("platforms: {}".format(platforms))

            k_map = KeyMapping(path)

            with self.context("File: {}".format(self.rel_path(path))):
                self._verify_keymap(k_map)

                conflicts = []
                for plat in platforms:
                    local_conflicts = k_map.find_conflicts(def_bindings[plat])
                    l.debug("#conflicts for %s on platform %s: %d",
                            self.rel_path(k_map.path), plat, len(local_conflicts))
                    # prevent duplicates while maintaining order
                    for conflict in local_conflicts:
                        if conflict not in conflicts:
                            conflicts.append(conflict)

                    # import pdb; pdb.set_trace()
                for conflict in conflicts:
                    if 'context' in conflict:
                        self.warn("The binding {} is also defined in default bindings "
                                  "but is masked with a 'context'".format(conflict['keys']))
                    else:
                        self.fail("The binding {} unconditionally overrides a default binding"
                                  .format(conflict['keys']))

    def _verify_keymap(self, k_map):
        allowed_keys = {'keys', 'command', 'args', 'context'}
        required_keys = {'keys', 'command'}

        idx_to_del = set()
        for i, binding in enumerate(k_map.data):
            with self.context("Binding: {}".format(json.dumps(binding))):
                keys = set(binding.keys())
                missing_keys = required_keys - keys
                if missing_keys:
                    self.fail("Binding is missing the keys {}".format(missing_keys))

                    # It would be useless to continue analyzing this entry,
                    # so schedule it for deletion
                    idx_to_del.add(i)

                supplementary_keys = keys - allowed_keys
                if supplementary_keys:
                    self.warn("Binding defines supplementary keys {}".format(supplementary_keys))

                if 'keys' in binding:
                    try:
                        norm_chords = k_map._verify_and_normalize_chords(binding['keys'])
                    except KeyMappingError as e:
                        self.fail(e.args[0])
                        idx_to_del.add(i)
                    else:
                        binding['keys'] = norm_chords

                # TODO verify 'context'

        # do actual deletion (in reverse)
        for i in sorted(idx_to_del, reverse=True):
            del k_map.data[i]


class KeyMappingError(ValueError):
    pass


class KeyMapping:

    _def_maps = None

    @classmethod
    def default_maps(cls):
        # type: Dict[str, KeyMapping]
        if not cls._def_maps:
            cls._def_maps = {plat: cls(DATA_PATH / fname)
                             for plat, fname in zip(PLATFORMS, PLATFORM_FILENAMES)}
            # Verify and normalize default maps
            for k_map in cls._def_maps.values():
                k_map._verify()

        return cls._def_maps

    def __init__(self, path):
        self.path = path
        self.data = self._load(path)

    def find_conflicts(self, other):
        return [binding for binding in self.data
                if other.get_for_chords(binding['keys'])]

    def get_for_chords(self, chords):
        return [binding for binding in self.data
                if binding['keys'] == chords]

    @classmethod
    def _load(cls, path):
        with path.open(encoding='utf-8') as f:
            return jsonc.loads(f.read())

    def _verify(self):
        for binding in self.data:
            binding['keys'] = self._verify_and_normalize_chords(binding['keys'])

    @classmethod
    def _verify_and_normalize_chords(cls, chords):
        modifiers = ("ctrl", "super", "alt", "shift")

        if not chords or not isinstance(chords, list):
            raise KeyMappingError("'keys' key is empty or not a list")
        norm_chords = []
        for key_chord in chords:
            chord_parts = []
            while True:
                modifier, plus, key_chord = key_chord.partition("+")
                if not key_chord:  # we're at the end
                    if plus:  # a chord with '+' as key
                        modifier = plus
                        plus = ""
                    # if not cls._verify_key(modifier):  # TODO
                    #     return None
                    chord_parts.sort(key=modifiers.index)
                    chord_parts.append(modifier)
                    break

                if modifier == "option":
                    modifier = "alt"
                if modifier not in modifiers:
                    raise KeyMappingError("Unrecognized modifier key '{}'".format(modifier))

                chord_parts.append(modifier)

            norm_chords.append("+".join(chord_parts))

        if norm_chords != chords:
            l.debug("normalized chords {!r} to {!r}".format(chords, norm_chords))
        return norm_chords

    # @classmethod
    # def _verify_key(cls, key):
    #     return True  # TODO
