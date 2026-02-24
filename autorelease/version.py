# This file vendored from Autorelease
import os
import subprocess

try:
    from configparser import (
        ConfigParser, Error as ConfigParserError, NoSectionError, NoOptionError
    )
except ImportError:
    # py2
    from ConfigParser import (
        ConfigParser, Error as ConfigParserError, NoSectionError, NoOptionError
    )

try:
    from ._installed_version import _installed_version
    from ._installed_version import _installed_git_hash
    from ._installed_version import _version_setup_depth
except ImportError:
    _installed_version = "Unknown"
    _installed_git_hash = "Unknown"
    _version_setup_depth = -1


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

def _seek_parent_dirs_for_file(filename):
    rel_directory = None
    my_dir = os.path.dirname(os.path.abspath(__file__))
    rel_directory_arr = []
    while not rel_directory:
        expected_dir = os.path.join(*rel_directory_arr) \
                if rel_directory_arr else '.'
        expected = os.path.join(expected_dir, filename)
        if os.path.isfile(os.path.normpath(expected)):
            rel_directory = expected_dir
        else:
            rel_directory_arr.append('..')

        if len(rel_directory_arr) > len(my_dir.split(os.sep)):
            rel_directory_arr = []
            break

    return rel_directory


def _find_rel_path_for_file(depth, filename):
    rel_directory = None
    if depth == 0:
        rel_directory = '.'
    elif depth >= 1:
        rel_directory = os.sep.join(['..'] * depth)
    else:
        rel_directory = _seek_parent_dirs_for_file(filename)

    if rel_directory:
        return os.path.normpath(os.path.join(rel_directory, filename))
    else:
        return None


def get_setup_cfg(directory, filename="setup.cfg"):
    """Load the setup.cfg as a dict-of-dict.

    Parameters
    ----------
    directory : str
        directory for setup.cfg, relative to cwd; default '.'
    filename : str
        filename for setup.cfg; default 'setup.cfg'
    """
    if isinstance(directory, int):
        rel_path = _find_rel_path_for_file(directory, filename)
        start_dir = os.path.abspath(os.path.dirname(__file__))
        setup_cfg = os.path.normpath(os.path.join(start_dir, rel_path))
    else:
        setup_cfg = os.path.join(directory, filename)

    conf = None
    if os.path.exists(setup_cfg):
        conf = ConfigParser()
        try:
            conf.read(setup_cfg)
        except ConfigParserError:
            conf = None

    return conf


def get_setup_value(default_value, directory, option, section='metadata',
                    filename="setup.cfg"):
    """Get a setup.cfg value or return the provided default.

    Parameters
    ----------
    default_value
        value to return when setup.cfg is missing or does not define field
    directory : str or int
        directory for setup.cfg (or search depth if int)
    option : str
        field name to retrieve from section
    section : str
        section name to query; default 'metadata'
    filename : str
        filename for setup.cfg; default 'setup.cfg'
    """
    value = default_value
    conf = get_setup_cfg(directory, filename)
    try:
        value = conf.get(section, option)
    except (NoSectionError, NoOptionError):
        pass  # option (or section) not defined in setup.cfg
    except AttributeError:
        pass  # no setup.cfg found (conf is None)
    return value


def get_setup_version(default_version, directory, filename="setup.cfg"):
    return get_setup_value(default_version, directory=directory,
                           option='version', section='metadata',
                           filename=filename)


def get_setup_name(default_name, directory, filename="setup.cfg"):
    return get_setup_value(default_name, directory=directory,
                           option='name', section='metadata',
                           filename=filename)


short_version = get_setup_version(_installed_version,
                                  directory=_version_setup_depth)
_git_version = get_git_version()
_is_repo = (_git_version != '' and _git_version != "Unknown")

if _is_repo:
    git_hash = _git_version
    full_version = short_version + "+g" + _git_version[:7]
    version = full_version
else:
    git_hash = "Unknown"
    full_version = short_version + "+g" + _installed_git_hash[:7] + '.install'
    version = short_version
