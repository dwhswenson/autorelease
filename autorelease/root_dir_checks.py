from __future__ import print_function
import sys
import os


def setup_is_release(setup, expected=True):
    """
    Returns
    -------
    bool or None :
        None if we can't tell
    """
    try:
        is_release = setup.IS_RELEASE
    except AttributeError:
        return None
    else:
        if is_release and expected:
            return ""
        elif not is_release and not expected:
            return ""
        else:
            return ("Unexpected value of setup.py IS_RELEASE. Found "
                    + str(is_release) + ".\n")


def requirements_consistency(setup, txt="requirements.txt",
                             conda_recipe=None):
    """
    Checks that the requirements defined in setup.py, requirements.txt, and
    (optionally) the conda recipe's meta.yaml file are all in agreement.
    Includes version checks (for pins) on requirements.txt and the conda
    recipe.
    """
    pass


def readme_rst_exists():
    """
    Checks that the README.rst file exists.

    This file should be read in as the long description in setup.py.
    """
    if os.path.isfile("README.rst"):
        return ""
    else:
        return "Missing README.rst file"
