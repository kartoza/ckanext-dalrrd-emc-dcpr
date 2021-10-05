FROM python:3.9-slim-bullseye

# Install security updates and system dependencies, then clean up
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get --yes upgrade && \
    apt-get install --yes --no-install-recommends tini && \
    # these are ckan dependencies, as reported in the ckan Dockerfile
    apt-get install --yes --no-install-recommends \
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
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser

# Install poetry
ENV POETRY_HOME=/tmp/poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - --no-modify-path
ENV PATH=$POETRY_HOME/bin:$PATH

# Run as non-root user
USER appuser

# Only copy the dependencies for now and install them
WORKDIR /app
COPY --chown appuser pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev


# Now install our code
COPY --chown=appuser . .
RUN poetry install --no-dev

# This allows us to get traces whenever some C code segfaults
ENV PYTHONFAULTHANDLER=1

# Compile python stuff to bytecode to improve startup times
RUN python -c "import compileall; compileall.compile_path(maxlevels=10)"
RUN python -m compileall /app/

ARG git_commit
ENV git_commit=$git_commit
RUN echo $git_commit > /git-commit.txt

# use tini as the init process
ENTRYPOINT ["tini", "-g", "--", "/entrypoint.sh"]