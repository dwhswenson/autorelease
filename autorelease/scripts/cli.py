import click

from autorelease.scripts.vendor import vendor_actions

@click.group()
def cli():
    pass


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
