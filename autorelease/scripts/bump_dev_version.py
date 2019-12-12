import argparse
import time

try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    # py2
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError


from json import JSONDecodeError

from packaging.version import Version
import requests

def get_latest_pypi(package, index="https://test.pypi.org/pypi"):
    url = "/".join([index, package, 'json'])
    req = requests.get(url)
    try:
        version = max([Version(v) for v in req.json()['releases'].keys()])
    except JSONDecodeError:
        # couldn't find a version, so we're okay
        version = "0.0.0.dev0"
    return str(version)

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

def shared_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", type=str,
                        default="https://test.pypi.org/pypi",
                        help="pypi index to search for versions")
    parser.add_argument("-c", "--conf", type=str, default="setup.cfg",
                        help="setup.cfg file to use")
    return parser
    parser.add_argument('--get-max', action='store_true')
    return parser

def get_version_info(conf_name, index):
    conf = ConfigParser()
    conf.read(conf_name)
    v_setup = conf.get('metadata', 'version')
    package = conf.get('metadata', 'name')
    v_pypi = get_latest_pypi(package, index)
    return conf, package, v_setup, v_pypi

def wait_for_max():
    parser = shared_parser()
    opts = parser.parse_args()

    found_desired = False
    while not found_desired:
        _, package, v_setup, v_pypi = get_version_info(opts.conf,
                                                       opts.index)
        print("Looking for version with base : %s" % v_setup)
        print("Maximum version on index: %s" % v_pypi)
        vv_setup = Version(v_setup)
        vv_pypi = Version(v_pypi)
        if vv_setup.base_version > vv_pypi.base_version:
            print("Waiting 5 seconds to see if package registers")
            time.sleep(5)
        elif vv_setup.base_version < vv_pypi.base_version:
            raise RuntimeError("Why is this version less than the index?")
        else:  # we are equal
            found_desired = True


def get_max():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=str)
    parser.add_argument("-i", "--index", type=str,
                        default="https://test.pypi.org/pypi",
                        help="pypi index to search for versions")
    opts = parser.parse_args()
    print(get_latest_pypi(opts.package, opts.index))


def main():
    parser = shared_parser()
    parser.add_argument("-o", "--output", type=str,
                        help="output file; defaults to same as input")
    parser.add_argument('--dry', action='store_true')
    opts = parser.parse_args()
    output = opts.conf if opts.output is None else opts.output

    conf, package, v_setup, v_pypi = get_version_info(opts.conf, opts.index)
    version_to_bump = select_version(v_pypi, v_setup)
    new_version = bump_dev_version(version_to_bump)

    print("Local version: ", v_setup)
    print("Remote version: ", v_pypi)
    print("Bumped version: ", new_version)

    if not opts.dry:
        conf.set('metadata', 'version', new_version)
        with open(output, 'w') as f:
            conf.write(f)

if __name__ == "__main__":
    main()
