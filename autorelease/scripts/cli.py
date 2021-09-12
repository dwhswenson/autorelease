import os
import click
import yaml

from autorelease.scripts.vendor import vendor_actions
from autorelease.scripts.check import run_checks
from autorelease import ReleaseNoteWriter


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
def cli():
    pass

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
@click.option('--conf', type=click.File('r'))
@click.option('--auth', type=click.File('r'))
@click.option('--since-release', type=str, default=None)
@click.option('-o', '--output', type=str)
def notes(conf, auth, since_release, output):
    config = load_config(conf)
    github_user = load_auth(auth)
    notes_conf = config['notes']
    notes_conf.update(github_user)
    notes_conf['project'] = config['project']
    writer = ReleaseNoteWriter(config=notes_conf)
    writer.write_release_notes(outfile=output)

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
