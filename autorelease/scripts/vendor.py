import string
try:
    import pathlib
except ImportError:  # py2
    import pathlib2 as pathlib
try:
    from importlib import resources as importlib_resources
except ImportError:  # py < 3.7
    import importlib_resources
from packaging.version import Version
import autorelease

import git
import re

def extract_github_owner_and_repo(url):
    github_url_re = r".*github.com:(?P<owner>.*)/(?P<repo>.*)"
    m = re.match(github_url_re, url)
    if m is None:
        raise ValueError(f"Unable to parse GitHub URL: {url}")
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
    if "owner" in config and "repo" in config:
        return config["owner"] + "/" + config["repo"]

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


def vendor(resources, base_path, relative_target_dir, substitutions,
           dry=False):
    for resource in resources:
        # Use importlib.resources to get the resource content
        try:
            # For Python 3.9+
            resource_files = importlib_resources.files('autorelease')
            resource_path = resource_files / resource
            with resource_path.open('r') as rfile:
                template_content = rfile.read()
        except AttributeError:
            # For Python 3.7-3.8
            with importlib_resources.path('autorelease', resource) as resource_path:
                with open(resource_path, mode='r') as rfile:
                    template_content = rfile.read()

        name = pathlib.Path(resource).name
        target_dir = base_path / relative_target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_loc = base_path / relative_target_dir / name
        # print(f"cp {resource} {target_loc}")
        template = string.Template(template_content)

        content = template.substitute(**substitutions)

        if dry:
            print(f"Would write to {target_loc}:")
            print(content)
        else:
            with open(target_loc, mode='w') as wfile:
                wfile.write(content)


def vendor_actions(base_path, owner_repo=None, dry=False):
    resources = ['autorelease-default-env.sh', 'autorelease-prep.yml',
                 'autorelease-gh-rel.yml', 'autorelease-deploy.yml']
    resources = ['gh_actions_stages/' + res for res in resources]
    target_dir = pathlib.Path('.github/workflows')
    if owner_repo:
        if owner_repo.count('/') != 1:
            raise ValueError("owner_repo must be in the format 'owner/repo'")
        owner, repo = owner_repo.split('/')
        if not owner or not repo:
            raise ValueError("Both owner and repo must be non-empty in 'owner/repo'")
        config = {"owner": owner, "repo": repo}
    else:
        config = None
    substitutions = get_substitution_mapping(config)
    vendor(resources, base_path, target_dir, substitutions, dry=dry)
