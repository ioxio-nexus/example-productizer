#!/usr/bin/env sh
#
# This file is for building the Python dependencies which frequently change
#

set -eu

# Set up working environment before everything else (it's quite spammy with -x)
. ~/.poetry/env

set -x

poetry install

echo
echo "PIP Dependency tree outside of virtualenv:"
echo
pipdeptree

echo
echo "PIP Dependency tree inside virtualenv:"
echo
poetry run pipdeptree

ls -lha