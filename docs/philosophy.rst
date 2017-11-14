.. _philosophy:

##########
Philosophy
##########

Part of running a software project involves managing the code repository.
This leads to issues of maintaining old code while simultaneously developing
new code, and avoiding dumping experimental code on user who just want
something that is stable. Version control systems, such as ``git``, go a
long way toward making this easier, but we developers still have to set (and
follow) some rules in order for this to work.

Over the years, developers have come up with a lot of different workflows
for these processes. A few that have been circulated are `GitFlow <>`_ and
`OneFlow <>`_. (And here are a few other articles on this topic).

Here, I'm going to describe my own approach. It takes some elements from
GitFlow, although it is not identical to it. The ``autorelease`` package was
written to facilitate this workflow; therefore I'll call the workflow
"AutoFlow." I've been using it in several of my own projects, and I hope it
will be of use to others.

.. note::

    I strongly prefer to work (and use AutoFlow) in a fork-based workflow.
    That is, there is a "central, official" repository, and forks for each
    developer. This way the number of branches in the central repository can
    be kept very small. Otherwise, one must distinguish between the
    long-lived branches (which is the focus here) and short-lived branches
    (feature branches, hotfixes). ``autorelease`` assumes you only run CI on
    long-lived branches and on the pull requests to them.

The central idea of AutoFlow is invariants. When thinking about the branches
in your (central) repository, what should be true whenever you look at these
branches? Setting rules makes it so that our branches become a sort of
contract with our users, and they know what to expect. This also facilitates
algorithmic checks: if we have invariants, we can use a computer to ensure
that we don't violate them.

Invariants and branches
=======================

The main invariant that I try to maintain is that branches are either
releases or not. The ``HEAD`` of a release branch never includes commits
that aren't in a release, and the ``HEAD`` of a non-release branch always
includes commits that aren't in a release.

These main categories define the invariants that ``autorelease`` uses to
check the code. Conceptually, we can distinguish different kinds of release
and non-release branches. These matter for the workflow, but not for the
``autorelease`` code. Within release branches, we can have several "support"
branches, plus one special branch which is called ``stable`` -- this is our
most recent release. Within nonrelease branches, we can have several
"future" branches, plus one "next release" branch. I prefer to set my
``master`` to the next release (others might call that ``dev`` and
use ``master`` where I use ``stable``).

As an example, let's say that I've just released code at 2.4.1, and I'm
still maintaining one support branch (based on release 1.3.1). However, I'm
also already developing 

============ ========== =================================== =============
Branch        released   base version                        branch name
============ ========== =================================== =============
support       True       release version (e.g., 1.3.1)       ``1.x``
stable        True       most recent release (e.g., 2.4.1)   ``stable``
development   False      next planned version (e.g., 2.5)    ``master``
future        False      next major version (e.g., 3.0)      ``3.0-dev``
============ ========== =================================== =============

Note that it is still possible to add features to the ``1.x`` support branch
and create a release 1.4. In fact, you could choose to have several
support branches: instead of only one called ``1.x``, you could have a
``1.3`` and a ``1.4``.  Personally, I'm only  only likely to have one
support branch at any time, although in theory you might have several.

Workflows
=========

So if this settles the invariants and defines our branches, the next
question is, how do I do this in practice? How do I maintain these
invariants?

This is where it becomes useful to have a step-by-step guide. We'll look at
several different workflows:

* Adding to the development branch
* Making a release
* Adding to a support branch
* Hotfixes for support branches

In the simplest workflow, you only need a ``master`` (development) and
``stable`` branch. We'll deal with merging to those branches first. Then
we'll move on to working with multiple release branches and multiple
future branches.

Adding to the development branch
--------------------------------

The workflow for adding to the (``master``) development branch is
straightforward:

1. Create a feature branch from ``master``
2. Write your code
3. Submit a pull request back to ``master``

This is probably what you're already doing.

Making a release
----------------

Making a release is a bit more complicated. Fortunately, ``autorelease`` is
here to make it easier for you.

The full procedure (which is largely automated by ``autorelease``) is:

1. Make a branch from ``master`` for the new release. Update set the
   ``IS_RELEASE`` flag in ``setup.py`` to ``True``, and update the version
   nummber where necessary.
2. Make a pull request against stable. Use the proposed release notes as the
   pull request description.
3. Test that the code can be merged into ``stable``.
4. Test that, after the code is merged into ``stable``, the resulting
   package will work (by uploading it to testpypi, downloading the resulting
   package, and running tests on that).
5. Once merged to ``stable``, create a release on GitHub. Add the release
   notes.
6. After the release has been made on GitHub (which creates a git tag
   associated with the release) upload the code (from the tag) to PyPI.

Note that with ``autorelease``, the first two steps must be done. Steps 3
and 4 are part of the automated tests of the pull request, and steps 5 and 6
are automated after the merge into stable. In practice, all you have to do
to make a release is update the code to reflect that is *is* a release and
make a PR (with release notes as description) into ``stable``. When it
passes tests, merge it in. All the rest is automatic.

Adding to a support/future branch
---------------------------------



Releasing from support branches
-------------------------------

