#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

######################################################################
# Node stage to deal with static asset construction
######################################################################
ARG PY_VER=3.11.11-slim-bookworm

# If BUILDPLATFORM is null, set it to 'amd64' (or leave as is otherwise).
ARG BUILDPLATFORM=${BUILDPLATFORM:-amd64}

# Include translations in the final build
ARG BUILD_TRANSLATIONS="false"

######################################################################
# rama-node-ci used as a base for building frontend assets and CI
######################################################################
FROM --platform=${BUILDPLATFORM} node:20-bullseye-slim AS rama-node-ci
ARG BUILD_TRANSLATIONS
ENV BUILD_TRANSLATIONS=${BUILD_TRANSLATIONS}
ARG DEV_MODE="false"           # Skip frontend build in dev mode
ENV DEV_MODE=${DEV_MODE}

COPY docker/ /app/docker/
# Arguments for build configuration
ARG NPM_BUILD_CMD="build"

# Install system dependencies required for node-gyp
RUN /app/docker/apt-install.sh build-essential python3 zstd

# Define environment variables for frontend build
ENV BUILD_CMD=${NPM_BUILD_CMD} \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Run the frontend memory monitoring script
RUN /app/docker/frontend-mem-nag.sh

WORKDIR /app/rama-frontend

# Create necessary folders to avoid errors in subsequent steps
RUN mkdir -p /app/rama/static/assets \
             /app/rama/translations

# Mount package files and install dependencies if not in dev mode
# NOTE: we mount packages and plugins as they are referenced in package.json as workspaces
# ideally we'd COPY only their package.json. Here npm ci will be cached as long
# as the full content of these folders don't change, yielding a decent cache reuse rate.
# Note that's it's not possible selectively COPY of mount using blobs.
RUN --mount=type=bind,source=./rama-frontend/package.json,target=./package.json \
    --mount=type=bind,source=./rama-frontend/package-lock.json,target=./package-lock.json \
    --mount=type=cache,target=/root/.cache \
    --mount=type=cache,target=/root/.npm \
    if [ "$DEV_MODE" = "false" ]; then \
        npm ci; \
    else \
        echo "Skipping 'npm ci' in dev mode"; \
    fi

# Runs the webpack build process
COPY rama-frontend /app/rama-frontend

######################################################################
# rama-node used for compile frontend assets
######################################################################
FROM rama-node-ci AS rama-node

# Build the frontend if not in dev mode
RUN --mount=type=cache,target=/root/.npm \
    if [ "$DEV_MODE" = "false" ]; then \
        echo "Running 'npm run ${BUILD_CMD}'"; \
        npm run ${BUILD_CMD}; \
    else \
        echo "Skipping 'npm run ${BUILD_CMD}' in dev mode"; \
    fi;

# Copy translation files
COPY rama/translations /app/rama/translations

# Build the frontend if not in dev mode
RUN if [ "$BUILD_TRANSLATIONS" = "true" ]; then \
        npm run build-translation; \
    fi; \
    rm -rf /app/rama/translations/*/*/*.po; \
    rm -rf /app/rama/translations/*/*/*.mo;


######################################################################
# Base python layer
######################################################################
FROM python:${PY_VER} AS python-base

ARG RAMA_HOME="/app/rama_home"
ENV RAMA_HOME=${RAMA_HOME}

RUN mkdir -p $RAMA_HOME
RUN useradd --user-group -d ${RAMA_HOME} -m --no-log-init --shell /bin/bash rama \
    && chmod -R 1777 $RAMA_HOME \
    && chown -R rama:rama $RAMA_HOME

# Some bash scripts needed throughout the layers
COPY --chmod=755 docker/*.sh /app/docker/

RUN pip install --no-cache-dir --upgrade uv

# Using uv as it's faster/simpler than pip
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"

######################################################################
# Python translation compiler layer
######################################################################
FROM python-base AS python-translation-compiler

ARG BUILD_TRANSLATIONS
ENV BUILD_TRANSLATIONS=${BUILD_TRANSLATIONS}

# Install Python dependencies using docker/pip-install.sh
COPY requirements/translations.txt requirements/
RUN --mount=type=cache,target=/root/.cache/uv \
    . /app/.venv/bin/activate && /app/docker/pip-install.sh --requires-build-essential -r requirements/translations.txt

COPY rama/translations/ /app/translations_mo/
RUN if [ "$BUILD_TRANSLATIONS" = "true" ]; then \
        pybabel compile -d /app/translations_mo | true; \
    fi; \
    rm -f /app/translations_mo/*/*/*.po; \
    rm -f /app/translations_mo/*/*/*.json;

######################################################################
# Python APP common layer
######################################################################
FROM python-base AS python-common

ENV RAMA_HOME="/app/rama_home" \
    HOME="/app/rama_home" \
    RAMA_ENV="production" \
    FLASK_APP="rama.app:create_app()" \
    PYTHONPATH="/app/pythonpath" \
    RAMA_PORT="8088"

# Copy the entrypoints, make them executable in userspace
COPY --chmod=755 docker/entrypoints /app/docker/entrypoints

WORKDIR /app
# Set up necessary directories and user
RUN mkdir -p \
      ${PYTHONPATH} \
      rama/static \
      requirements \
      rama-frontend \
      apache_rama.egg-info \
      requirements \
    && touch rama/static/version_info.json

# Install Playwright and optionally setup headless browsers
ARG INCLUDE_CHROMIUM="true"
ARG INCLUDE_FIREFOX="false"
RUN --mount=type=cache,target=${RAMA_HOME}/.cache/uv \
    if [ "$INCLUDE_CHROMIUM" = "true" ] || [ "$INCLUDE_FIREFOX" = "true" ]; then \
        uv pip install playwright && \
        playwright install-deps && \
        if [ "$INCLUDE_CHROMIUM" = "true" ]; then playwright install chromium; fi && \
        if [ "$INCLUDE_FIREFOX" = "true" ]; then playwright install firefox; fi; \
    else \
        echo "Skipping browser installation"; \
    fi

# Copy required files for Python build
COPY pyproject.toml setup.py MANIFEST.in README.md ./
COPY rama-frontend/package.json rama-frontend/
COPY scripts/check-env.py scripts/

# keeping for backward compatibility
COPY --chmod=755 ./docker/entrypoints/run-server.sh /usr/bin/

# Some debian libs
RUN /app/docker/apt-install.sh \
      curl \
      libsasl2-dev \
      libsasl2-modules-gssapi-mit \
      libpq-dev \
      libecpg-dev \
      libldap2-dev

# Copy compiled things from previous stages
COPY --from=rama-node /app/rama/static/assets rama/static/assets

# TODO, when the next version comes out, use --exclude rama/translations
COPY rama rama
# TODO in the meantime, remove the .po files
RUN rm rama/translations/*/*/*.po

# Merging translations from backend and frontend stages
COPY --from=rama-node /app/rama/translations rama/translations
COPY --from=python-translation-compiler /app/translations_mo rama/translations

HEALTHCHECK CMD curl -f "http://localhost:${RAMA_PORT}/health"
CMD ["/app/docker/entrypoints/run-server.sh"]
EXPOSE ${RAMA_PORT}

######################################################################
# Final lean image...
######################################################################
FROM python-common AS lean

# Install Python dependencies using docker/pip-install.sh
COPY requirements/base.txt requirements/
RUN --mount=type=cache,target=${RAMA_HOME}/.cache/uv \
    /app/docker/pip-install.sh --requires-build-essential -r requirements/base.txt
# Install the rama package
RUN --mount=type=cache,target=${RAMA_HOME}/.cache/uv \
    uv pip install .
RUN python -m compileall /app/rama

USER rama

######################################################################
# Dev image...
######################################################################
FROM python-common AS dev

# Debian libs needed for dev
RUN /app/docker/apt-install.sh \
    git \
    pkg-config \
    default-libmysqlclient-dev

# Copy development requirements and install them
COPY requirements/*.txt requirements/
# Install Python dependencies using docker/pip-install.sh
RUN --mount=type=cache,target=${RAMA_HOME}/.cache/uv \
    /app/docker/pip-install.sh --requires-build-essential -r requirements/development.txt
# Install the rama package
RUN --mount=type=cache,target=${RAMA_HOME}/.cache/uv \
    uv pip install .

RUN uv pip install .[postgres]
RUN python -m compileall /app/rama

USER rama

######################################################################
# CI image...
######################################################################
FROM lean AS ci
USER root
RUN uv pip install .[postgres]
USER rama
CMD ["/app/docker/entrypoints/docker-ci.sh"]
