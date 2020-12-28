import yaml

from packaging.version import Version

from autorelease.version_checks import parse_versions
from autorelease.utils import import_setup
from autorelease import DefaultCheckRunner

def checker_from_yaml_dict(release_check):
    repo_path = release_check.get('repo_path', '.')
    release_branches = release_check.get('release-branches', [])
    release_tag_format = release_check.get('release-tag', "v{BASE_VERSION}")
    versions = parse_versions(release_check['versions'])
    base_version = Version(list(versions.values())[0]).base_version
    release_tag = release_tag_format.format(BASE_VERSION=base_version)
    setup = import_setup(directory=repo_path)

    checker = DefaultCheckRunner(
        versions=versions,
        setup=setup,
        repo_path=repo_path
    )
    checker.release_branches = release_branches + [release_tag]
    return checker


def run_checks(yml, branch=None, event=None, allow_patch_skip=False):
    dct = yaml.load(yml, Loader=yaml.FullLoader)
    release_check = dct['release-check']
    checker = checker_from_yaml_dict(release_check)
    if branch is None and event is None:
        branch, event = checker.get_branch_event_from_github_env()

    tests = checker.select_tests_from_branch_event(branch, event,
                                                   allow_patch_skip)
    checker.run_as_test(tests)


if __name__ == "__main__":
    with open("autorelease.yml", 'r') as f:
        run_checks(f)

