import yaml
import re
import os
import importlib.util

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
    spec = importlib.util.spec_from_file_location(
        'setup', os.path.join(directory, 'setup.py')
    )
    setup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup)
    return setup
