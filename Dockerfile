# ---- BUILD ENVIRONMENT ----- #

# python:3.6-alpine3.11 on 2020-01-30
FROM python@sha256:c0b79a54025287948507652ba97bf4100aed05809998b2f45b4e39cc99ada21a

ENV ENV="development" \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    USER="api" \
    GROUP="api" \
    UID=1000 \
    GID=1000 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION="1.0.2" \
    WORKON_HOME="/.venv"

# Initial setup for build environment
WORKDIR /src/productizer
ADD docker-build-setup.sh ./
RUN sh docker-build-setup.sh

# Add minimal things for installing dependencies
USER ${USER}

# GOTCHA: These will be owned by root --chown= does not take env variables
ADD pyproject.toml poetry.lock docker-build-deps.sh ./
RUN sh docker-build-deps.sh

# ---- RUNTIME ENVIRONMENT ----- #

# python:3.6-alpine3.11 on 2020-01-30
FROM python@sha256:c0b79a54025287948507652ba97bf4100aed05809998b2f45b4e39cc99ada21a

ENV ENV="development" \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    USER="api" \
    GROUP="api" \
    UID=1000 \
    GID=1000 \
    PYTHONUNBUFFERED=1 \
    WORKON_HOME="/.venv"

COPY --from=0 /home/${USER}/.poetry /home/${USER}/.poetry/
COPY --from=0 ${WORKON_HOME} ${WORKON_HOME}

WORKDIR /src/productizer
ADD pyproject.toml poetry.lock docker-runtime-setup.sh ./
RUN sh docker-runtime-setup.sh

ADD . ./

USER ${USER}
ENTRYPOINT ["sh", "docker-runtime-entrypoint.sh"]
