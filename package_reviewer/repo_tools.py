from collections import namedtuple
import functools
import logging
import re
import tempfile
import zipfile

from .lib import semver


__all__ = ('tags', 'SemVerTag', 'semver_tags', 'latest_ref', 'download')

l = logging.getLogger(__name__)


# Cache a repos' tags
@functools.lru_cache()
def tags(repo):
    tags = tuple(repo.tags())
    l.debug("tags: %s", tags)
    return tags


SemVerTag = namedtuple("SemVerTag", "version tag")


# More caching
@functools.lru_cache()
def semver_tags(repo):
    semver_tags = []
    for tag in tags(repo):
        # do some smart-ass stripping here
        stripped_name = re.sub(r"^(v|st[23]?-v?)", '', tag.name)
        try:
            ver = semver.SemVer(stripped_name)
        except ValueError:
            l.debug("'%s' tag is not a semantic version", tag.name)
        else:
            semver_tags.append(SemVerTag(ver, tag))
    l.debug("semver tags: %s", semver_tags)

    return tuple(semver_tags)


def latest_ref(repo):
    latest_version = max(semver_tags(repo), key=lambda x: x.version, default=None)
    if latest_version is None:
        # TODO determine a repo's default branch?
        # Alternatively, have this specified by CLI.
        # By default, PC downloads master branch anyway.
        return "heads/master"
    else:
        return "tags/{}".format(latest_version.tag.name)


# TODO tarfile does not work for some reason
def download(repo, ref, dirpath):
    # if dirpath is None:
    #     dirpath = Path(tempfile.mkdtemp(suffix="_" + repo.name))

    with tempfile.TemporaryFile() as f:
        l.info("Downloading package...")
        repo.archive('zipball', path=f, ref=ref)  # 'tarball'
        res = f.seek(0)
        assert res == 0

        l.debug("Extracting to '%s'...", dirpath)
        zipf = zipfile.ZipFile(f)  # tarf = tarfile.TarFile(fileobj=f)
        try:
            zipf.extractall(path=str(dirpath))
        except Exception:
            l.exception("Couldn't extract zipfile contents")
            return None

        # Because all archives from github are nested another level,
        # we need to find out what the name of that folder is.
        namelist = zipf.namelist()
        if not namelist:
            l.error("zip file is empty")
            return None
        subfolder_name, slash, _ = namelist[0].partition('/')
        assert slash

    target_path = dirpath / subfolder_name
    l.info("Downloaded package to '%s'", target_path)
    return target_path
