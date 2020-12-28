import click

from autorelease.scripts.vendor import vendor_actions
from autorelease.scripts.check import run_checks

@click.group()
def cli():
    pass

@cli.command()
@click.option('--conf', type=click.File('r'), default='autorelease.yml')
@click.option('--branch', default=None)
@click.option('--event', default=None)
def check(conf, branch, event):
    run_checks(conf, branch, event)

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
