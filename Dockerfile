FROM python:3.9-slim-bullseye

# Install security updates and system dependencies, then clean up
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get --yes upgrade && \
    apt-get install --yes --no-install-recommends tini && \
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
    apt-get --yes clean && \
    rm -rf /var/lib/apt/lists/*

# download poetry
RUN curl --silent --show-error --location \
    https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py > /opt/get-poetry.py

# Create a normal non-root user so that we can use it to run
RUN useradd --create-home appuser

# Compile python stuff to bytecode to improve startup times
RUN python -c "import compileall; compileall.compile_path(maxlevels=10)"

USER appuser

RUN mkdir /home/appuser/app  && \
#    mkdir /home/appuser/third-party && \
    python opt/get-poetry.py --yes --version 1.1.11

ENV PATH="$PATH:/home/appuser/.poetry/bin"

# Only copy the dependencies for now and install them
WORKDIR /home/appuser/app
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

# get ckan
#WORKDIR /home/appuser/third-party
#RUN curl --silent --show-error --location \
#    https://github.com/ckan/ckan/archive/refs/tags/ckan-2.9.4.tar.gz > ckan-2.9.4.tar.gz && \
#    tar --extract --verbose --file=ckan-2.9.4.tar.gz

WORKDIR /home/appuser/app

# Install ckan
#RUN poetry add ../third-party/ckan-ckan-2.9.4

# Now install our code
COPY --chown=appuser:appuser . .
RUN poetry install --no-dev

EXPOSE 5000

# This allows us to get traces whenever some C code segfaults
ENV PYTHONFAULTHANDLER=1

# Write git commit identifier into the image
ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT
RUN echo $GIT_COMMIT > /home/appuser/git-commit.txt

ENV CKAN_INI=/home/appuser/ckan.ini

# Compile python stuff to bytecode to improve startup times
RUN poetry run python -c "import compileall; compileall.compile_path(maxlevels=10)"

# use tini as the init process
ENTRYPOINT ["tini", "-g", "--", "poetry", "run", "docker_entrypoint"]

CMD ["launch-gunicorn"]
