import os
import click
import yaml

from autorelease.scripts.vendor import vendor_actions
from autorelease.scripts.check import run_checks
# from autorelease import ReleaseNoteWriter
from autorelease.gh_api4.notes4 import NotesWriter, prs_since_latest_release

import logging


def _find_first_file(pathlist):
    for p in pathlist:
        if os.path.exists(p):
            return p
    return None

def load_yaml(user_input, default_pathlist):
    if user_input is not None:
        dct = yaml.load(user_input, Loader=yaml.FullLoader)
    else:
        filename = _find_first_file(default_pathlist)
        if filename is None:
            raise RuntimeError("No config file could be found")
        with open(filename, mode='r') as f:
            dct = yaml.load(f, Loader=yaml.FullLoader)

    return dct

def load_config(user_input):
    paths = [
        ".autorelease.yml",
        "autorelease.yml",
        os.path.join(".autorelease", "autorelease.yml"),
        os.path.join(".autorelease", "conf.yml"),
    ]
    return load_yaml(user_input, paths)

def load_auth(user_input):
    paths = [
        os.path.join(os.path.expanduser("~"), ".autorelease-auth.yml"),
        os.path.join(".autorelease", "auth.yml"),
        os.path.join(".autorelease", "autorelease-auth.yml"),
        ".autorelease-auth.yml",
        "autorelease-auth.yml",
    ]
    return load_yaml(user_input, paths)


@click.group()
@click.option("--loglevel", type=str, default="WARNING")
def cli(loglevel):
    logging.basicConfig(level=getattr(logging, loglevel))
    logger = logging.getLogger("autorelease")
    logger.setLevel(getattr(logging, loglevel))

@cli.command()
@click.option('--conf', type=click.File('r'))
@click.option('--branch', default=None)
@click.option('--event', default=None)
def check(conf, branch, event):
    dct = load_config(conf)
    run_checks(dct, branch, event)

@cli.command()
@click.option('--conf', type=click.File('r'))
def config(conf):
    from pprint import pprint
    config = load_config(conf)
    pprint(config)

@cli.command()
@click.option('--auth', type=click.File('r'))
def auth(auth):
    from pprint import pprint
    auth = load_auth(auth)
    pprint(auth)


@cli.command()
@click.option('--conf', type=click.File('r'))
@click.option('--auth', type=click.File('r'))
def notes(conf, auth):
    config = load_config(conf)
    github_user = load_auth(auth)
    target_branch = config['repo'].get('dev-branch', 'main')
    notes_conf = config['notes']
    notes_conf.update(github_user)
    notes_conf['project'] = config['project']
    category_labels = {
        lab['label']: lab['heading'] for lab in notes_conf['labels']
    }
    topics = {}
    for label in notes_conf['labels']:
        if tops := label.get('topics'):
            topic_dict = {top['label']: top['name'] for top in tops}
            topics[label['label']] = topic_dict

    writer = NotesWriter(
        category_labels=category_labels,
        topics=topics,
        standard_contributors=notes_conf['standard_contributors']
    )
    new_prs = prs_since_latest_release(
        owner=config['project']['repo_owner'],
        repo=config['project']['repo_name'],
        auth=(None, github_user['github_user']['token']),
        target_branch=target_branch,
    )
    print(writer.write(new_prs))

@click.group()
def vendor():
    pass

@vendor.command()
def actions():
    print("vendoring actions")
    vendor_actions(base_path='.')

cli.add_command(vendor)

if __name__ == "__main__":
    cli()
