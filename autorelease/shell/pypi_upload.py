#!/usr/bin/env python
from __future__ import print_function

import argparse
import subprocess  # let's work on removing this

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', type=str, default="pypi")
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('--tag', type=str, default="")
    return parser.parse_args()

def run_in_shell(cmd, dry=False):
    print(cmd)
    if dry:
        return
    else:
        return subprocess.call(cmd, shell=True)


class Distributor(object):
    def __init__(self, commands=None, tag="", dry=False):
        self.commands = commands
        if self.commands is None:
            self.commands = ['sdist', 'bdist_wheel']
        self.tag = tag
        self.dry = dry

    def checkout_tag(self):
        if self.tag == "":
            return
        cmd = "git fetch --tags && git checkout tags/" + self.tag
        run_in_shell(cmd, self.dry)

    def make_distribution(self):
        # https://stackoverflow.com/questions/935111 ??
        cmd = "python setup.py " + " ".join(self.commands)
        run_in_shell(cmd, self.dry)

    def get_sha256(self):
        # replace with hashlib (built-in anyone)
        cmd = "openssl sha256 dist/*"
        run_in_shell(cmd, self.dry)

class Uploader(object):
    def __init__(self, repo_label="pypi", dry=False):
        self.repo_label = repo_label
        self.repo_url = self.get_repo_url(repo_label)
        self.dry = dry

    @staticmethod
    def get_repo_url(label):
        base_dict = {
            'pypi': "",
            'testpypi': "https://test.pypi.org/legacy/",
            'test': "https://test.pypi.org/legacy/"
        }
        return base_dict[label]

    def twine_upload(self):
        upload_url = ""
        if self.repo_url != "":
            upload_url = "--repository-url " + self.repo_url

        cmd = "twine upload " + upload_url + " dist/*"
        run_in_shell(cmd, self.dry)


if __name__ == "__main__":
    opts = parse()
    distrib = Distributor(tag=opts.tag, dry=opts.dry)
    upload = Uploader(repo_label=opts.repository, dry=opts.dry)

    distrib.checkout_tag()
    distrib.make_distribution()
    distrib.get_sha256()
    upload.twine_upload()
