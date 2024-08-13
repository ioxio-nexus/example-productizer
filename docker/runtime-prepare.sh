#!/usr/bin/env bash
#
# This step is for initializing the runtime environment
#

# shellcheck disable=SC2039
set -exuo pipefail

# Set up PYTHONPATH for the main package. Only this module will be installed
su "${USER}" -c ". ${POETRY_HOME}/env; poetry install --compile"

# Ensure user cannot edit the filesystem contents
chown -R root:root .
