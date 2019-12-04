import os
import glob
import ast
import sys

import subprocess
import inspect

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # py2

from setuptools import setup


def is_release(version):
    allowed_releases = os.getenv('AUTORELEASE_RELEASE_TYPES',
                                 'pre a b rc post').split()
    # this approach may be completely changed -- idea is to identify all
    # alphabet-character substrings
    start = 0
    end = 0
    all_alpha = []
    len_vers = len(version)
    while end <= len_vers:
        #print(start, end, version[start:end], version[start:end].isalpha())
        if not version[start:end + 1].isalpha() or end == len_vers:
            if end - start > 1:
                all_alpha.append(version[start:end])
            start = end
        end += 1

    #print(all_alpha)
    return all([val in AUTORELEASE_RELEASE_TYPES for val in all_alpha])


class VersionPyFinder(object):
    _VERSION_PY_FUNCTIONS = ['get_git_version', 'get_setup_cfg']
    def __init__(self, filename='version.py', max_depth=2):
        self.filename_base = filename
        self.max_depth = max_depth
        self.depth = None
        self.filename = os.getenv("AUTORELEASE_VERSION_PY",
                                  self._first_eligible())
        self.functions = self._get_functions(self.filename)

    def _find_files(self):
        all_files = glob.glob("**/" + self.filename_base, recursive=True)
        meets_depth = [fname for fname in all_files
                       if len(fname.split(os.sep)) < self.max_depth + 1]
        return meets_depth

    def _is_eligible(self, filename):
        with open(filename, mode='r') as f:
            contents = f.read()

        tree = ast.parse(contents)
        # we requrie that our functions be defined at module level -- we
        # know that's how we wrote them, at least!
        all_functions = [node.name for node in tree.body
                         if isinstance(node, ast.FunctionDef)]
        return all(func in all_functions
                   for func in self._VERSION_PY_FUNCTIONS)

    def _first_eligible(self):
        all_files = self._find_files()
        for fname in all_files:
            if self._is_eligible(fname):
                return fname
        return None

    @property
    def version_setup_depth(self):
        def get_depth(fname):
            return len(os.path.abspath(fname).split(os.sep))

        # we assume thta setup.py is in the same dir as setup.cfg
        diff = get_depth(self.filename) - get_depth(__file__)
        return diff

    def _get_functions(self, filename):
        with open(self.filename, mode='r') as f:
            contents = f.read()

        locs = dict(globals())
        exec(contents, locs)
        return {f: locs[f] for f in self._VERSION_PY_FUNCTIONS}


def write_installed_version_py(filename="_installed_version.py",
                               src_dir=None):
    version_finder = VersionPyFinder()
    directory = os.path.dirname(version_finder.filename)
    depth = version_finder.version_setup_depth
    get_git_version = version_finder.functions['get_git_version']
    get_setup_cfg = version_finder.functions['get_setup_cfg']

    installed_version = os.path.join(directory, "_installed_version.py")
    content = "_installed_version = '{vers}'\n"
    content += "_installed_git_hash = '{git}'\n"
    content += "_version_setup_depth = {depth}\n"

    # question: if I use the __file__ attribute in something I compile from
    # here, what is the file?
    my_dir = os.path.abspath(os.path.dirname(__file__))
    conf = get_setup_cfg(directory=my_dir, filename='setup.cfg')
    # conf = get_setup_cfg(directory=my_dir, filename='new_setup.cfg')
    version = conf['metadata']['version']
    git_rev = get_git_version()

    if src_dir is None:
        src_dir = conf['metadata']['name']

    with open (os.path.join(src_dir, filename), 'w') as f:
        f.write(content.format(vers=version, git=git_rev, depth=depth))

if __name__ == "__main__":
    # TODO: only write version.py under special circumstances
    write_installed_version_py()
    # write_version_py(os.path.join('autorelease', 'version.py'))
    setup()

