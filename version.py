#!/usr/bin/env python3

import semver
import subprocess


def git_version():
    """ get the version from git. Can be
        - X.Y.Z if a tag is set on the current HEAD
        - X.Y.Z-<count>-g<commitid> otherwise where
            - X.Y.Z is the latest version tag found
            - <count> is the number of commits since then
            - <commitid> is the current HEAD commitid
    """
    cmd = "git describe --tags --match=[0-9]*.[0-9]*.[0-9]*"
    p = subprocess.run(cmd.split(" "), capture_output=True, check=True)
    return p.stdout.decode("utf-8")


def version(git):
    """ get a semver version out of the input git version (see git_version())
        - if a X.Y.Z tag is set on the current HEAD, we'll use this
        - else we'll use X.Y.Z+1-<count>.<commitid> to respect semver
    """
    # X.Y.Z-<count>-g<commitid> is not a valid semver.
    # X.Y.Z-<count>.<commitid> is. <count>.<commitid> is then a prerelease field
    v = semver.VersionInfo.parse(git.replace("-g", "."))
    if v.prerelease:
        # semver prerelase are supposed to show build increments *prior* to a release
        # so we're bumping the patch number to show what the next release would be
        # this allows correct version ordering
        v = v.replace(patch=v.patch + 1)
    return str(v)


if __name__ == "__main__":
    print(version(git_version()))
