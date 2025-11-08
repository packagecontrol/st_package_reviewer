import argparse
import json
import sys


"""
Tooling: diff two registry files and print added/changed/removed names.

"""


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Diff two registry files and report added/changed/removed package names.",
    )
    parser.add_argument('--base-file', required=True, help='Path to base registry JSON to diff')
    parser.add_argument('--target-file', required=True, help='Path to target registry JSON to diff')
    parser.add_argument(
        '-z',
        action='store_true',
        help='Separate entries with NUL (\\0) instead of newlines')

    args = parser.parse_args(argv)

    with open(args.base_file, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    with open(args.target_file, 'r', encoding='utf-8') as f:
        target_data = json.load(f)

    base_map = extract_registry_map(base_data)
    target_map = extract_registry_map(target_data)

    base_names = set(base_map.keys())
    target_names = set(target_map.keys())

    removed = sorted(base_names - target_names)
    added = sorted(target_names - base_names)

    common = base_names & target_names
    changed = []
    for name in common:
        b = base_map.get(name)
        t = target_map.get(name)
        if _normalize_package(b) != _normalize_package(t):
            changed.append(name)
    changed.sort()

    # Print summary to stderr
    eprint(
        "::notice title=CHANGES ::"
        f"Removed {_format_oxford_list(removed)}, "
        f"changed {_format_oxford_list(changed)}, "
        f"added {_format_oxford_list(added)}."
    )

    if args.z:
        for name in changed + added:
            print(name, end="\0")

    return 0


def extract_registry_map(registry_json) -> dict:
    """Return mapping name->package for the expected registry schema.

    Expected structure:
      {
        "repositories": [ ... ],
        "packages": [ {"name": ...}, ... ]
      }
    """
    if not isinstance(registry_json, dict):
        eprint("::error ::registry JSON must be an object with 'packages' list")
        sys.exit(2)

    pkgs = registry_json.get('packages')
    if not isinstance(pkgs, list):
        eprint("::error ::registry JSON must contain 'packages' as a list")
        sys.exit(2)

    result = {}
    for item in pkgs:
        if isinstance(item, dict) and 'name' in item:
            result[item['name']] = item
    return result


def _format_oxford_list(items):
    n = len(items)
    if n == 0:
        return "(none)"
    if n == 1:
        return items[0]
    if n == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _normalize_package(pkg: dict) -> dict:
    """Return a normalized copy of a package for meaningful comparisons.

    - Drop ephemeral fields that differ across refs (e.g. 'source').
    - Sort list fields where ordering is not semantically meaningful.
    - Sort release entries for stable ordering.
    """
    if not isinstance(pkg, dict):
        return pkg

    # Shallow copy, "source" is a URL that can include a commit sha
    norm = {k: v for k, v in pkg.items() if k != 'source'}

    # Normalize simple list fields
    for key in ('labels', 'previous_names'):
        if key in norm and isinstance(norm[key], list):
            try:
                norm[key] = sorted(norm[key])
            except TypeError:
                # Mixed types; fall back to stringified sort
                norm[key] = sorted(norm[key], key=lambda x: str(x))

    # Normalize releases: sort entries by stable key
    if 'releases' in norm and isinstance(norm['releases'], list):
        rels = norm['releases']

        # Brutally convert a complete dict to a key
        def rel_key(d):
            if isinstance(d, dict):
                # JSON string as a stable key
                try:
                    return json.dumps(d, sort_keys=True)
                except Exception:
                    return str(d)
            return str(d)

        norm['releases'] = sorted(rels, key=rel_key)

    return norm


if __name__ == '__main__':
    sys.exit(main())
