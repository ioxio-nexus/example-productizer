#!/usr/bin/env sh
#
# This step is for initializing the runtime environment
#

set -exu

# Create runtime user
addgroup -g ${GID} -S ${GROUP}

if [[ "${DEVELOPMENT:-0}" == "1" ]]; then
  adduser -u ${UID} -S ${USER} -G ${GROUP} -G wheel -D
else
  adduser -u ${UID} -S ${USER} -G ${GROUP} -D
fi
sed -i -E 's@api:(.*):/sbin/nologin@api:\1:/bin/ash@' /etc/passwd
chmod +x /home/${USER}/.poetry/bin/*

# Allow ${USER} to edit contents while installing things
chown -R ${USER}:${GROUP} .

# Poetry configuration
su ${USER} -c '. ~/.poetry/env; poetry config virtualenvs.in-project false'
su ${USER} -c ". ~/.poetry/env; poetry config virtualenvs.path ${WORKON_HOME}"

# Ensure user cannot edit the filesystem contents
chown -R root:root .

