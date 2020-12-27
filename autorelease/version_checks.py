from __future__ import print_function

import re
import packaging.version as vers

from autorelease.version import get_setup_version  # reuse the vendored
from autorelease.utils import conda_recipe_version

version_getters = {
    'setup-cfg': lambda path: get_setup_version(None, path),
    'conda': conda_recipe_version,
}

default_args = {
    'setup-cfg': ['.']
}

def parse_versions(versions_list):
    versions = {}
    for version_type in versions_list:
        if isinstance(version_type, dict):
            version_type, arg = list(version_type.items())[0]
            args = [arg]
        else:
            args = default_args.get(version_type, [])

        versions[version_type] = version_getters[version_type](*args)
    return versions


class VersionReleaseChecks(object):
    def __init__(self, versions, strictness='strict'):
        self.versions = versions
        self.strictness = strictness

    @staticmethod
    def _version(version, strictness):
        if strictness == 'strict':
            return version
        elif strictness == 'loose':
            return vers.Version(version).public
        elif strictness == 'base-only':
            return vers.Version(version).base_version
        else:
            raise ValueError("Bad strictness: " + str(strictness))
        # TODO: I'm sure I can create more!

    def consistency(self, desired_version=None, include_package=False,
                    strictness=None):
        """Checks that the versions are consistent

        Parameters
        ----------
        desired_version: str
            optional; the version that all of these should match
        include_package: bool
            whether to check the special 'package' version for consistency
            (default False)
        strictness: str

        """
        keys_to_check = list(self.versions.keys())
        if not include_package and 'package' in keys_to_check:
            keys_to_check.remove('package')

        if desired_version is None:
            # if we have to guess, we trust setup.py
            try:
                desired_version = self.versions['setup.py']
            except KeyError:
                desired_version = self.versions[keys_to_check[0]]

        if strictness is None:
            strictness = self.strictness
        desired = self._version(desired_version, strictness)

        error_keys = []
        for key in keys_to_check:
            test = self._version(self.versions[key], strictness)
            if test != desired:
                error_keys += [key]

        # make the error message
        msg = ""
        for key in error_keys:
            msg += "Error: desired {d} != {v} ({k})\n".format(
                d=str(desired),
                v=str(self.versions[key]),
                k=str(key)
            )
        return msg

    @staticmethod
    def is_release(version, expected=True):
        version = str(version)
        msg = ""
        if expected is vers.Version(version).is_prerelease:
            msg += "Version " + str(version) + " is "
            if expected:
                msg += "not "
            msg += "a release version\n"

        return msg
