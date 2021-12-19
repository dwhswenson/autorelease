import string
try:
    import pathlib
except ImportError:  # py2
    import pathlib2
import pkg_resources
from packaging.version import Version
import autorelease

import git
import re

def extract_github_owner_and_repo(url):
    github_url_re = ".*github.com:(?P<owner>.*)/(?P<repo>.*)"
    m = re.match(github_url_re, url)
    owner = m.group('owner')
    repo = m.group('repo')
    if repo.endswith('.git'):
        repo = repo[:-4]
    return owner, repo


def guess_parent_repository(repo_name='.'):
    """
    Guess the repository to consider as the "main" repo, based on remotes.

    This returns GitHub repo owner and repo name for the 'upstream' remote
    if it exists, otherwise 'origin' if it exists. If neither exists,
    returns None, None.

    Returns
    -------
    owner : str
        owner of the GitHub repo
    repo : str
        name of the GitHub repo
    """
    repo = git.Repo(repo_name)
    parent = None
    try:
        parent = repo.remotes.upstream
    except AttributeError:
        try:
            parent = repo.remotes.origin
        except AttributeError:
            pass

    if parent is None:
        return None, None
    else:
        return extract_github_owner_and_repo(parent.url)


def _get_github_repo(config):
    # TODO: this guessing should be a backup plan; get info from config if
    # available
    owner, repo = guess_parent_repository('.')
    if owner is None or repo is None:
        raise RuntimeError("Unable to determine repository")
    return owner + "/" + repo


def get_substitution_mapping(config=None):
    version = Version(autorelease.version.version).base_version
    return {
        'VERSION': version,
        'GITHUB_REPO': _get_github_repo(config)
    }


def vendor(resources, base_path, relative_target_dir, substitutions):
    for resource in resources:
        orig_loc = pkg_resources.resource_filename('autorelease', resource)
        name = pathlib.Path(orig_loc).name
        target_dir = base_path / relative_target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_loc = base_path / relative_target_dir / name
        # print(f"cp {orig_loc} {target_loc}")
        with open(orig_loc, mode='r') as rfile:
            template = string.Template(rfile.read())

        with open(target_loc, mode='w') as wfile:
            wfile.write(template.substitute(**substitutions))

def vendor_actions(base_path):
    resources = ['autorelease-default-env.sh', 'autorelease-prep.yml',
                 'autorelease-gh-rel.yml', 'autorelease-deploy.yml']
    resources = ['gh_actions_stages/' + res for res in resources]
    target_dir = pathlib.Path('.github/workflows')
    substitutions = get_substitution_mapping()
    vendor(resources, base_path, target_dir, substitutions)

