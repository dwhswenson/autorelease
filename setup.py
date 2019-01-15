"""
setup.py for autorelease
"""
import os
import subprocess
import inspect
from setuptools import setup

####################### USER SETUP AREA #################################
# * VERSION: base version (do not include .dev0, etc -- that's automatic)
# * IS_RELEASE: whether this is a release
VERSION = "0.0.11"
IS_RELEASE = True

DEV_NUM = 0  # always 0: we don't do public (pypi) .dev releases
PRE_TYPE = ""  # a, b, or rc (although we rarely release such versions)
PRE_NUM = 0

# REQUIREMENTS should list any required packages
REQUIREMENTS=['packaging', 'pyyaml', 'gitpython', 'future', 'requests']

# PACKAGES should list any subpackages of the code. The assumption is that
# package.subpackage is located at package/subpackage
PACKAGES=['autorelease', 'autorelease.tests', 'autorelease.scripts']

# This DESCRIPTION is only used if a README.rst hasn't been made from the
# markdown version
DESCRIPTION="""Tools to keep the release process clean, based on my own
release procedures. For details, see the documentation.
"""
SHORT_DESCRIPTION="Tools to keep the release process clean"

# note: leave the triple quotes on separate lines from the classifiers
CLASSIFIERS="""
Development Status :: 1 - Planning
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Topic :: Software Development :: Testing
"""
####################### USER SETUP AREA #################################


# * VERSION: the release version number
# * __version__: ?? how is this used ??
# * PACKAGE_VERSION: the version used in setup.py info
PACKAGE_VERSION = VERSION
if PRE_TYPE != "":
    PACKAGE_VERSION += "." + PRE_TYPE + str(PRE_NUM)
if not IS_RELEASE:
    PACKAGE_VERSION += ".dev" + str(DEV_NUM)
__version__ = PACKAGE_VERSION

if os.path.isfile('README.rst'):
    DESCRIPTION = open('README.rst').read()

################################################################################
# Writing version control information to the module
################################################################################
def get_git_version():
    """
    Return the git hash as a string.

    Apparently someone got this from numpy's setup.py. It has since been
    modified a few times.
    """
    # Return the git revision as a string
    # copied from numpy setup.py
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        with open(os.devnull, 'w') as err_out:
            out = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=err_out, # maybe debug later?
                                   env=env).communicate()[0]
        return out

    try:
        git_dir = os.path.dirname(os.path.realpath(__file__))
        out = _minimal_ext_cmd(['git', '-C', git_dir, 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = 'Unknown'

    return GIT_REVISION

# TODO: this may get moved into another file
VERSION_PY_CONTENT = """
# This file is automatically generated by setup.py
\"\"\"
Version info for autorelease.

``full_version`` gives the most information about the current state. It is
always the short (PEP440) version string, followed by a git hash as
``+gGITHASH``. If the install is not in a live git repository, that hash is
followed by ``.install``, and represents the commit that was installed. In a
live repository, it represents the active state.
\"\"\"

import os
import subprocess

# this is automatically generated from the code in setup.py
%(git_version_code)s

short_version = '%(version)s'
version = '%(version)s'
installed_git_hash = '%(git_revision)s'
full_version = version + '+g' + installed_git_hash[:7] + '.install'
release = %(is_release)s
git_hash = 'Unknown'  # default

if not release:
    git_hash = get_git_version()
    if git_hash != '' and git_hash != 'Unknown':
        full_version = version + '+g' + git_hash[:7]

    version = full_version
"""

def write_version_py(filename):
    # Adding the git rev number needs to be done inside write_version_py(),
    # otherwise the import of numpy.version messes up the build under Python 3.
    git_version_code = inspect.getsource(get_git_version)
    if os.path.exists('.git'):
        GIT_REVISION = get_git_version()
    else:
        GIT_REVISION = 'Unknown'

    content = VERSION_PY_CONTENT % {
        'version': PACKAGE_VERSION,
        'git_revision': GIT_REVISION,
        'is_release': str(IS_RELEASE),
        'git_version_code': str(git_version_code)
    }

    with open(filename, 'w') as version_file:
        version_file.write(content)


################################################################################
# Installation
################################################################################
if __name__ == "__main__":
    write_version_py(os.path.join('autorelease', 'version.py'))
    setup(
        name="autorelease",
        author="David W.H. Swenson",
        author_email="dwhs@hyperblazer.net",
        version=PACKAGE_VERSION,
        license="LGPL-2.1+",
        url="http://github.com/dwhswenson/autorelease",
        packages=PACKAGES,
        package_dir={p: '/'.join(p.split('.')) for p in PACKAGES},
        package_data={},
        ext_modules=[],
        scripts=[],
        entry_points={
            'console_scripts': [
                'autorelease-release = autorelease.scripts.release:main'
            ]
        },
        description=SHORT_DESCRIPTION,
        long_description=DESCRIPTION,
        platforms=['Linux', 'Mac OS X', 'Unix', 'Windows'],
        install_requires=REQUIREMENTS,
        requires=REQUIREMENTS,
        tests_require=["pytest", "pytest-cov", "python-coveralls"],
        classifiers=CLASSIFIERS.split('\n')[1:-1]
    )


