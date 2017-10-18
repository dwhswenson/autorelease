import yaml

def conda_recipe_version(recipe_file):
    with open(recipe_file) as f:
        dct = yaml.load(f.read())
    return dct['package']['version']
