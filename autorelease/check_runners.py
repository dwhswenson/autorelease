from __future__ import print_function
import sys
import os
import textwrap
import argparse
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
        self.output.write(str(method.__name__) + "... ")
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

    def run_as_test(self, tests=None):
        n_fails = self.run(tests)
        if n_fails > 0:
            exit(1)


class DefaultCheckRunner(CheckRunner):
    def __init__(self, versions, setup, repo_path='.', output=None):
        self.version_checks = autorelease.VersionReleaseChecks(
            versions=versions,
            strictness='strict'
        )
        self.setup = setup
        self.git_repo_checks = autorelease.GitReleaseChecks(
            repo_path=repo_path
        )
        version_0 = list(versions.values())[0]
        self.desired_version = vers.Version(version_0)
        super(DefaultCheckRunner, self).__init__(output=output)
        self.consistency_test = (
            self.version_checks.consistency, [],
            {'include_package': False}
        )
        self.tests = [self.consistency_test]
        self.release_branches = ['stable']
        self.tag_branch = \
            self.git_repo_checks.tag_from_version(self.desired_version)


    def _is_release_tests(self, expected):
        return [
            (self.version_checks.is_release, [],
             {'version': self.desired_version,
              'expected': expected}),
            (autorelease.setup_is_release, [],
             {'setup': self.setup,
              'expected': expected})
        ]

    def _reasonable_desired_version_test(self, allow_equal,
                                         allow_patch_skip=False):
        print("allow equal ", allow_equal)
        print("allow patch skip", allow_patch_skip)
        return [
            (
                self.git_repo_checks.reasonable_desired_version, [],
                {'desired_version': self.desired_version,
                 'allow_equal': allow_equal,
                 'allow_patch_skip': allow_patch_skip}
            )
        ]

    @staticmethod
    def _get_branch_name(branch_name):
        if branch_name.startswith('refs/heads/'):
            branch = branch_name[11:]
        elif branch_name.startswith('refs/tags/'):
            branch = branch_name[10:]
        else:
            branch = branch_name

        return branch

    def select_tests(self):
        print(os.environ.get("GITHUB_ACTION"))
        if os.environ.get("GITHUB_ACTION", None):
            tests = self.select_test_from_github_env()
        else:
            tests = self.select_tests_from_sysargs()
        return tests


    def select_tests_from_sysargs(self):
        # TODO: this can be cleaned up by separating reusable parts
        parser = argparse.ArgumentParser()
        parser.add_argument('--branch', type=str)
        parser.add_argument('--event', type=str)
        parser.add_argument('--allow-patch-skip', action='store_true',
                            default=False)
        opts = parser.parse_args()

        branch = self._get_branch_name(opts.branch)
        return self.select_tests_from_branch_event(branch, opts.event,
                                                   opts.allow_patch_skip)

    def get_branch_event_from_github_env(self):
        event = os.environ.get("GITHUB_EVENT_NAME", None)
        ref = os.environ.get("GITHUB_REF", None)
        pr_ref = os.environ.get("GITHUB_BASE_REF", None)
        print(ref, pr_ref)
        print(os.environ.get("GITHUB_HEAD_REF", None))
        if event == "pull_request" and pr_ref is not None:
            branch = pr_ref
        elif event != "pull_request":
            branch = ref
        else:
            raise RuntimeError("PR without branch?")
        branch = self._get_branch_name(branch)
        return branch, event

    def select_test_from_github_env(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--allow-patch-skip', action='store_true',
                            default=False)
        opts = parser.parse_args()
        branch, event = self.get_branch_event_from_github_env()
        print(branch, event)
        return self.select_tests_from_branch_event(branch, event,
                                                   opts.allow_patch_skip)


    def select_tests_from_branch_event(self, branch, event, allow_patch_skip):
        if branch in self.release_branches:
            print("TESTING AS RELEASE")
            allow_equal = (event == 'cron'
                           or event == 'schedule'
                           or branch == self.tag_branch)
            tests = (self.tests
                     + self._reasonable_desired_version_test(
                         allow_equal=allow_equal,
                         allow_patch_skip=allow_patch_skip)
                     + self._is_release_tests(expected=True))
        else:
            print("TESTING AS NONRELEASE")
            tests = (self.tests
                     + self._reasonable_desired_version_test(False)
                     + self._is_release_tests(expected=False))

        return tests
