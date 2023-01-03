FROM python:3.9-slim-bullseye

# Install security updates and system dependencies, then clean up
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get --yes upgrade && \
    # these are our own dependencies and utilities
    apt-get install --yes --no-install-recommends \
      net-tools \
      procps \
      tini && \
    # these are ckan dependencies, as reported in the ckan Dockerfile
    apt-get install --yes --no-install-recommends \
      libmagic1 \
      libpq-dev \
      libxml2-dev \
      libxslt-dev \
      libgeos-dev \
      libssl-dev \
      libffi-dev \
      postgresql-client \
      build-essential \
      git-core \
      wget \
      curl && \
    # these are ckanext-spatial dependencies \
    apt-get install --yes --no-install-recommends \
      proj-bin \
      python-dev \
      libxslt1-dev \
      libgeos-c1v5  \
      zlib1g-dev && \
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

# download poetry
RUN curl --silent --show-error --location \
    https://install.python-poetry.org > /opt/install-poetry.py

# Create a normal non-root user so that we can use it to run
RUN useradd --create-home appuser

# Compile python stuff to bytecode to improve startup times
RUN python -c "import compileall; compileall.compile_path(maxlevels=10)"

USER appuser

RUN mkdir /home/appuser/app  && \
    mkdir /home/appuser/data && \
    python opt/install-poetry.py --yes --version 1.1.11

ENV PATH="$PATH:/home/appuser/.local/bin" \
    # This allows us to get traces whenever some C code segfaults
    PYTHONFAULTHANDLER=1 \
    CKAN_INI=/home/appuser/ckan.ini

# Only copy the dependencies for now and install them
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

EXPOSE 5000

# Now install our code
COPY --chown=appuser:appuser . .
RUN poetry install --no-dev

# Write git commit identifier into the image
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT
RUN echo $GIT_COMMIT > /home/appuser/git-commit.txt


# Compile python stuff to bytecode to improve startup times
RUN poetry run python -c "import compileall; compileall.compile_path(maxlevels=10)"

# use tini as the init process
ENTRYPOINT ["tini", "-g", "--", "poetry", "run", "docker_entrypoint"]

CMD ["launch-gunicorn"]
