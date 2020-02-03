#!/usr/bin/env sh
#
# This file is for launching the application in the container
#

set -eu

# Set up working environment before everything else (it's quite spammy with -x)
. ~/.poetry/env

set -x

if [[ "${DEVELOPMENT:-0}" == "1" ]]; then
  poetry run uvicorn app.main:app --host 0.0.0.0 --reload
else
  poetry run uvicorn app.main:app --host 0.0.0.0
fi
