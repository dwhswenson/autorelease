#/usr/bin/env python
from __future__ import print_function
import sys
import argparse

import setup
#import contact_map
from autorelease import DefaultCheckRunner, conda_recipe_version

repo_path = '.'
versions = {
    #'package': contact_map.version.version,
    'setup.py': setup.PACKAGE_VERSION,
    'conda-recipe': conda_recipe_version('devtools/conda-recipe/meta.yaml'),
}

RELEASE_BRANCHES = ['stable']
RELEASE_TAG = "v" + setup.PACKAGE_VERSION

if __name__ == "__main__":
    checker = DefaultCheckRunner(
        versions=versions,
        setup=setup,
        repo_path='.'
    )
    checker.release_branches = RELEASE_BRANCHES + [RELEASE_TAG]
    tests = checker.select_tests_from_sysargs()

    skip = []
    skip = [checker.git_repo_checks.reasonable_desired_version]
    for test in skip:
        skip_test = [t for t in tests if t[0] == test][0]
        tests.remove(skip_test)

    n_fails = checker.run_as_test(tests)
