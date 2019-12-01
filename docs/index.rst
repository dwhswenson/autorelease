.. autorelease documentation master file, created by
   sphinx-quickstart on Wed Oct 18 03:17:40 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Autorelease
===========

Autorelease is several things at once. It is:

* a set of Travis configs that can be imported to automate a cautious
  approach to releasing on PyPI
* a suite of tests to ensure that the Travis configs are behaving as desired
* a setup.py that can be used across many projects after simple
  customization
* a "one true version" approach to keep your version string in the fewest
  places possible
* useful scripts to handle things related to automating releases, such as
  automatically drafting release notes based on GitHub PR tags

Each of these things is individually useful, but the parts work together to
make something greater than their sum.

.. toctree::
   :maxdepth: 2

   philosophy



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
