[![Documentation Status](https://readthedocs.org/projects/autorelease/badge/?version=latest)](http://autorelease.readthedocs.io/en/latest/?badge=latest)
[![Linux Build](https://travis-ci.org/dwhswenson/autorelease.svg?branch=master)](https://travis-ci.org/dwhswenson/autorelease)
[![Windows Build](https://ci.appveyor.com/api/projects/status/ox0c6u5gobk5ksat/branch/master?svg=true)](https://ci.appveyor.com/project/dwhswenson/autorelease/branch/master)

# Autorelease

Tools for keeping release behavior clean. Includes:

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
