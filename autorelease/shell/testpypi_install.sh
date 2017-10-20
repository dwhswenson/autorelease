#!usr/bin/env bash

PACKAGE=$1

# prepare conda environment
ENVIRONMENT="test_$PACKAGE"
conda create -y --name $ENVIRONMENT python=$CANONICAL_PYTHON
source activate $ENVIRONMENT

# install any special requirements

pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $PACKAGE

# install test requirements
pip install pytest

# run tests
py.test --pyargs $PACKAGE -v  || exit 1

# remove the environment
source deactivate
conda remove -y --name $ENVIRONMENT --all
