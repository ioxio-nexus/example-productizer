# ---- BUILD ENVIRONMENT ----- #

FROM digitallivinginternational/python-base:ubuntu-python3.9 as build

WORKDIR /src/productizer

ADD docker/build-prepare.sh /src/docker/build-prepare.sh
RUN bash /src/docker/build-prepare.sh

ADD pyproject.toml poetry.lock ./
ADD docker/build-setup.sh /src/docker/build-setup.sh
RUN --mount=type=cache,target=/home/${USER}/.cache bash /src/docker/build-setup.sh


# ---- RUNTIME ENVIRONMENT ----- #

FROM digitallivinginternational/python-base:ubuntu-python3.9 as runtime

COPY --from=build ${WORKON_HOME} ${WORKON_HOME}

WORKDIR /src/productizer
ADD . ./

RUN bash docker/runtime-prepare.sh

USER ${USER}
EXPOSE 8000
ENTRYPOINT ["bash", "docker/runtime-entrypoint.sh"]
