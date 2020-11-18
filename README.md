[![Documentation Status](https://readthedocs.org/projects/autorelease/badge/?version=latest)](http://autorelease.readthedocs.io/en/latest/?badge=latest)
[![Linux Build](https://travis-ci.org/dwhswenson/autorelease.svg?branch=master)](https://travis-ci.org/dwhswenson/autorelease)
[![Windows Build](https://ci.appveyor.com/api/projects/status/ox0c6u5gobk5ksat/branch/master?svg=true)](https://ci.appveyor.com/project/dwhswenson/autorelease/branch/master)

# Autorelease

Release management for GitHub and continuous integration, based on branches.
The basic philosophy is to maintain development branches (which always have
development versions of the code) and release branches (which always have
release versions of the code). The workflow for a release is therefore:

1. Update the version for release and make a PR to a stable branch; the top
   post will be the release notes.
2. Merge the PR.

That's it.

When you make the PR to a stable branch, the CI will deploy the package to
testpypi, and re-download it and test it again. This ensures that you don't
publish broken packages. After you merge to the stable branch, the CI will cut
a new release on GitHub, and then release on PyPI.

Tools included:

* Travis config imports and scripts to automatically test-deploy on testpypi,
  then cut a GitHub release, then deploy to PyPI.
* Vendor-able `version.py` that gives one true location for version
  (`setup.cfg`) while also enabling developer installs to give full and correct
  version information.
* Vendor-able `setup.py` that keeps all user-required information in the
  `setup.cfg`.
* Script to draft release notes based on labels on merged PRs.

If you're a Python developer who uses Travis and GitHub, Autorelease handles
everything related to releasing to PyPI.
