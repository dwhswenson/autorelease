import yaml
import re

def conda_recipe_version(recipe_file):
    with open(recipe_file) as f:
        dct = yaml.load(f.read(), Loader=yaml.FullLoader)
    return dct['package']['version']

def github_url_to_owner_repo(url):
    pattern = ".*github.com[\:\/]([^\/]+)\/(.*)\.git"
    match = re.match(pattern, url)
    return match.groups()
