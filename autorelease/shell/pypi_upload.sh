#/bin/bash/env bash

set -e

is_test=0
tag_name=""

# based on https://stackoverflow.com/a/7680682
optspec="-:"
while getopts -- "$optspec" optchar; do
    case "${optchar}" in
        -)
            case "$OPTARG" in
                test)
                    is_test=1
                    ;;
                tag)
                    tag_name="${!OPTIND}"; OPTIND=$(( $OPTIND + 1 ))
                    ;;
                tag=*)
                    tag_name=${OPTARG#*=}
                    ;;
                *)
                    if [ "$OPTERR" != 1 ] || [ "${optspec:0:1}" = ":" ]; then
                        echo "Unknown argument: '-${OPTARG}'" >&2
                    fi
                    ;;
            esac
    esac
done

# must have either is_test or tag set
if [ $is_test -eq 0 ]; then
    if [ "$tag_name" = "" ]; then
        echo "Error: must set either --test or --tag"
        exit 1
    fi
fi


if [ $is_test -eq 1 ]; then
    UPLOAD_URL="--repository-url https://test.pypi.org/legacy/"
    # bump build number if necessary
else
    UPLOAD_URL=""
fi

if [ "$tag_name" != "" ]; then
   git fetch --tags
   git checkout tags/$tag_name
fi

python setup.py sdist bdist_wheel

twine upload $UPLOAD_URL dist/*

openssl sha256 dist/*

python setup.py clean; rm -rf build/ sdist/
