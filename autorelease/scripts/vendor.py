import pkg_resources
import pathlib
import shutil

import click

def vendor(resources, base_path, relative_target_dir):
    for resource in resources:
        orig_loc = pkg_resources.resource_filename('autorelease', resource)
        name = pathlib.Path(orig_loc).name
        target_dir = base_path / relative_target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        target_loc = base_path / relative_target_dir / name
        # print(f"cp {orig_loc} {target_loc}")
        shutil.copy(orig_loc, target_loc)

def vendor_actions(base_path):
    resources = ['autorelease-default-env.sh', 'autorelease-prep.yml',
                 'autorelease-gh-rel.yml', 'autorelease-deploy.yml']
    resources = ['gh_actions_stages/' + res for res in resources]
    target_dir = pathlib.Path('.github/workflows')
    vendor(resources, base_path, target_dir)

