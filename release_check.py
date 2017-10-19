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
NONRELEASE_BRANCHES = ['master']

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--branch', type=str)
    return parser

if __name__ == "__main__":
    parser = make_parser()
    opts = parser.parse_args()

    checker = DefaultCheckRunner(
        versions=versions,
        setup=setup,
        repo_path='.'
    )

    if opts.branch == 'master':
        tests = checker.nonrelease_tests
    elif opts.branch == 'stable':
        tests = checker.release_tests
    else:
        print("Unknown branch " + str(opts.branch))

    #n_fails = checker.run(checker.nonrelease_tests)
    n_fails = checker.run_as_test(tests)

    # tests that the current repo is consistent
    #check(version.consistency)
    #check(version.is_release, str(desired))
    #check(version.is_release, str(desired), expected=False)
    #check(git_repo.in_required_branch, 'stable')
    #check(git_repo.reasonable_desired_version, desired.base_version)
    #check(setup_is_release, setup)
    #check(setup_is_release, setup, expected=False)
    #check(readme_rst_exists)
