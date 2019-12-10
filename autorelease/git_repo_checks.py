import git  # GitPython
import packaging.version as vers

def skipped_version(old_version, new_version, allow_patch_skip=False):
    old_major, old_minor, old_patch = old_version
    new_major, new_minor, new_patch = new_version

    bad_update = False

    if new_major == old_major:
        if new_minor == old_minor:
            if not allow_patch_skip and new_patch != old_patch + 1:
                bad_update = True

        elif new_patch != 0 and new_minor != old_minor + 1:
            bad_update = True

    elif new_minor != 0 != new_patch and new_major != old_major + 1:
        bad_update = True

    return bad_update


class GitReleaseChecks(object):
    def __init__(self, repo_path='.'):
        self.repo_path = repo_path
        self.repo = git.Repo(self.repo_path)
        self.stable_branch = 'stable'
        self.dev_branch = 'master'

    @staticmethod
    def tag_from_version(version):
        return "v" + str(version)

    def in_required_branch(self, required_branch='stable'):
        msg = ""
        current_branch = self.repo.active_branch.name
        if current_branch != required_branch:
            msg = ("Current branch is '" + str(current_branch)
                   + "'; should be in '" + str(required_branch) + "'\n")
        return msg

    def _versions_from_tags(self):
        # assume tags are format vM.m.p_build
        # this takes the version (before the '_') and drops the preceding v
        tag_versions = [t.name.split('_')[0][1:] for t in self.repo.tags]
        # TODO: may be better to replace with regex for reusability
        versions = []
        for version in tag_versions:
            try:
                v = vers.Version(version)
            except vers.InvalidVersion:
                pass
            else:
                versions.append(v)
        return versions
        # return [vers.Version(v) for v in tag_versions]

    def reasonable_desired_version(self, desired_version, allow_equal=False,
                                  allow_patch_skip=False):
        """
        Determine whether the desired version is a reasonable next version.

        Parameters
        ----------
        desired_version: str
            the proposed next version name
        """
        try:
            desired_version = desired_version.base_version
        except:
            pass
        (new_major, new_minor, new_patch) = \
                map(int, desired_version.split('.'))

        tag_versions = self._versions_from_tags()
        if not tag_versions:
            # no tags yet, and legal version is legal!
            return ""
        max_version = max(self._versions_from_tags()).base_version
        parts = list(map(int, str(max_version).split('.')))
        parts += [0] * (3 - len(parts))
        old_major, old_minor, old_patch = parts

        update_str = str(max_version) + " -> " + str(desired_version)

        v_desired = vers.Version(desired_version)
        v_max = vers.Version(max_version)

        if allow_equal and v_desired == v_max:
            return ""

        if v_desired < v_max:
            return ("Bad update: New version doesn't increase on last tag: "
                    + update_str + "\n")

        bad_update = skipped_version((old_major, old_minor, old_patch),
                                     (new_major, new_minor, new_patch),
                                     allow_patch_skip)

        msg = ""
        if bad_update:
            msg = ("Bad update: Did you skip a version from "
                   + update_str + "?\n")

        return msg
