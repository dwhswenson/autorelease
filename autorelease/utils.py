import yaml
import re
import os
import sys

def conda_recipe_version(recipe_file):
    with open(recipe_file) as f:
        dct = yaml.load(f.read(), Loader=yaml.FullLoader)
    return dct['package']['version']

def github_url_to_owner_repo(url):
    pattern = ".*github.com[\:\/]([^\/]+)\/(.*)\.git"
    match = re.match(pattern, url)
    return match.groups()


def import_setup(directory='.'):
    """Return the imported setup.py from the given directory"""
    if sys.version_info > (3, ):
        return _import_setup_py3(directory)
    else:
        return _import_setup_py2(directory)


def _import_setup_py2(directory):
    import imp
    return imp.load_source('setup', os.path.join(directory, 'setup.py'))


def _import_setup_py3(directory):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'setup', os.path.join(directory, 'setup.py')
    )
    setup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup)
    return setup
