#!/usr/bin/env bash
#
# WARNING!
# ========
#
# THIS FILE IS NOT USED IN RUNTIME, ONLY WHILE BUILDING DOCKER IMAGES
# DO NOT ADD ANYTHING RUNTIME OR ENVIRONMENT SPECIFIC HERE
#

# shellcheck disable=SC2039
set -exuo pipefail

# Allow ${USER} to install python dependencies
chown -R "${USER}":"${GROUP}" /src

su "${USER}" -c ". ${POETRY_HOME}/env; poetry install --no-root --compile"
