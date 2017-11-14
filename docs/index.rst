.. autorelease documentation master file, created by
   sphinx-quickstart on Wed Oct 18 03:17:40 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

autorelease
===========

The ``autorelease`` package is designed to facilitate the release and
management of Python packages. By default, it tests based on the "AutoFlow"
approach, described on the :ref:`Philosophy Page <philosophy>`. However, the
tests used can be selected to fit a user's preferred approach.

When used in full, the ``autorelease`` package, with the AutoFlow approach,
reduces the release process to making a PR for the release and writing
release notes. In the context of a package hosted on GitHub and using
Travis-CI for continuous integration, everything else (including packaging
and upload to PyPI) is completely automated. Even a test of the package (by
uploading to testpypi) is performed before uploading the official version to
PyPI.

.. toctree::
   :maxdepth: 2

   philosophy



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
