import argparse
try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    # py2
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from packaging.version import Version
import requests

def get_latest_pypi(package, index="https://test.pypi.org/pypi"):
    url = "/".join([index, package, 'json'])
    req = requests.get(url)
    version = req.json()['info']['version']
    return version

def _strip_dev(version_str):
    version = Version(version_str)  # to normalize
    return str(version).split('.dev')[0]

def bump_dev_version(version_str):
    version = Version(version_str)
    if version.is_devrelease:
        dev_str = ".dev" + str(version.dev + 1)
        v_base, _ = str(version).split('.dev')
        out_v = v_base + dev_str
        pass
    else:
        out_v = version.public + ".dev0"
    return out_v

def select_version(v_pypi, v_setup):
    vv_pypi = _strip_dev(v_pypi)
    vv_setup = _strip_dev(v_setup)
    if Version(vv_setup) > Version(vv_pypi):
        return v_setup
    elif Version(vv_setup) == Version(vv_pypi):
        return v_pypi
    else:
        raise RuntimeError("Why does pypi have a newer version than setup?")

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", type=str,
                        default="https://test.pypi.org/pypi",
                        help="pypi index to search for versions")
    parser.add_argument("-c", "--conf", type=str, default="setup.cfg",
                        help="setup.cfg file to use")
    parser.add_argument("-o", "--output", type=str,
                        help="output file; defaults to same as input")
    return parser

def main():
    parser = make_parser()
    opts = parser.parse_args()
    output = opts.conf if opts.output is None else opts.output
    conf = ConfigParser()
    conf.read(opts.conf)
    v_setup = conf.get('metadata', 'version')
    package = conf.get('metadata', 'name')
    v_pypi = get_latest_pypi(package, opts.index)
    version_to_bump = select_version(v_pypi, v_setup)
    new_version = bump_dev_version(version_to_bump)
    conf.set('metadata', 'version', new_version)
    with open(output, 'w') as f:
        conf.write(f)

if __name__ == "__main__":
    main()
