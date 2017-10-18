from __future__ import print_function
import sys
import os
import re
import textwrap

import yaml
import git  # GitPython
import packaging.version as vers

import autorelease

class CheckRunner(object):
    def __init__(self, output):
        self.output = output or sys.stdout
        self.tests = []
        self.wrapper = textwrap.TextWrapper(width=78, initial_indent=" "*4,
                                            subsequent_indent=" "*4)

    def __call__(self, method, *args, **kwargs):
        """Generic method to turn other methods into tests.
        """
        self.output.write(str(method.func_name) + "... ")
        msg = method(*args, **kwargs)
        fail = 0
        if bool(msg):
            fail = 1
            self.output.write("FAIL\n")
            self.output.write(self.wrapper.fill(msg) + '\n')
        else:
            self.output.write("PASS\n")
        return fail

    def run(self, tests=None):
        tests = tests or self.tests  # take first non-None
        n_fails = 0
        for (method, args, kwargs) in tests:
            n_fails += self(method, *args, **kwargs)
        return n_fails


class DefaultReleaseCheckRunner(CheckRunner):
    def __init__(self, versions, repo_path='.', strictness='strict',
                 output=None):
        pass


class DefaultNonReleaseCheckRunner(CheckRunner):
    def __init__(self, versions, setup, repo_path='.', strictness='strict',
                 output=None):
        self.version_checks = autorelease.VersionReleaseChecks(
            versions=versions,
            strictness=strictness
        )
        self.git_repo_checks = autorelease.GitReleaseChecks(
            repo_path=repo_path
        )
        self.setup = setup
        self.desired_version = vers.Version(versions['setup.py'])
        super(DefaultNonReleaseCheckRunner, self).__init__(output=output)
        self.tests = [
            (
                self.version_checks.consistency, [],
                {'include_package': False}
            ),
            (
                self.version_checks.is_release, [],
                {'version': self.desired_version,
                 'expected': False}
            ),
            (
                self.git_repo_checks.in_required_branch, [],
                {'required_branch': 'master'}
            ),
            (
                self.git_repo_checks.reasonable_desired_version, [],
                {'desired_version': self.desired_version}
            ),
            (
                autorelease.setup_is_release, [],
                {'setup': self.setup,
                 'expected': False}
            )
        ]
