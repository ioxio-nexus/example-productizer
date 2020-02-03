#!/usr/bin/env sh
#
# This file is for installing the larger dependencies that rarely change such
# as OS packages, utilities and so on.
#

set -exu

# Set up user accounts
addgroup -g ${GID} -S ${GROUP}
adduser -u ${UID} -S ${USER} -G ${GROUP} -G wheel -D
# Allow su - user
sed -i -E "s@${USER}:(.*):/sbin/nologin@${USER}:\1:/bin/ash@" /etc/passwd

# Setting up dependencies
apk add --virtual build-dependencies \
  curl \
  gcc \
  g++ \
  make \
  musl-dev

# Ensure the WORKON_HOME exists, is empty and owned by ${USER}
if [[ ! -d "${WORKON_HOME}" ]]; then
  mkdir "${WORKON_HOME}"
fi
rm -rf "${WORKON_HOME:?}"/*
chown -R ${USER}:${GROUP} "${WORKON_HOME}"

# Installing some more clear deps
pip install --upgrade pip pipdeptree

# Install some things only for development
if [[ "${DEVELOPMENT:-0}" == "1" ]]; then

    # See https://www.hiroom2.com/2018/08/23/alpinelinux-3-8-sudo-en/ for
    # more information.
    apk add sudo
    # edit /etc/sudoers and delete comment at the %wheel.
    sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
    # Lock out root account with passwd -l
    passwd -l root
    # delete root password with passwd -d.
    passwd -d root
fi

# Install Poetry ${POETRY_VERSION} for ${USER}
su - ${USER} -c "curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python"
su - ${USER} -c '. ~/.poetry/env; poetry config virtualenvs.in-project false'
su - ${USER} -c ". ~/.poetry/env; poetry config virtualenvs.path ${WORKON_HOME}"

# Allow the next script to run as ${USER}
chown -R ${USER}:${GROUP} /src/productizer
