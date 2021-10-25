# ckanext-dalrrd-emc-dcpr

This is a [ckan](https://ckan.org) extension that implements the Electronic
Metadata Catalog for South Africa's Department of Agriculture, Land Reform
and Rural Development (DALRRD). It also contains additional utilities,
useful for running the full EMC.

## Installation

While this project can be installed standalone, it is primarily meant to be
used together with docker.

### docker standalone installation

Ideally, you should be able to pull prebuilt images from dockerhub:

https://hub.docker.com/r/kartoza/ckanext-dalrrd-emc-dcpr

```
docker pull kartoza/ckanext-dalrrd-emc-dcpr:main
```

Alternatively, you can also build the image locally by using the provided
build script:

```
cd docker
./build.sh
```

After having the image, use it to create containers. In order to be properly
recognized, your config files must be mounted at `/home/appuser/ckan.ini`
and `/home/appuser/who.ini`. For example, when running standalone:

  ```
  docker run \
      --rm \
      --volume=/home/myuser/my-ckan.ini:/home/appuser/ckan.ini \
      --volume=/home/myuser/who.ini:/home/appuser/who.ini \
      kartoza/ckanext-dalrrd-emc-dcpr:main
  ```


The provided `Dockerfile` has the following peculiarities:

- It **requires** you to mount the ckan configuration files in order to work;

- Uses [poetry](https://python-poetry.org/) to install Python packages and
  manage their environment;

- A custom docker entrypoint script implemented in Python. It has access to
  the poetry env and can be called by running `poetry run docker_entrypoint`;

- The entrypoint script waits for ckan's environment to be available,
  including waiting some time for the database, solr and redis services to
  become available. However, it **does not perform automatic database
  migrations** nor static files refresh;

- Uses [gunicorn](https://gunicorn.org/) as the Python app server.


### Standalone (non-docker) installation

To install ckanext-dalrrd-emc-dcpr, make sure CKAN is already installed on
your virtual environment if not, follow the

https://docs.ckan.org/en/2.9/maintaining/installing/install-from-source.html

guide to install CKAN, then follow the below steps:

1. Activate your CKAN virtual environment, for example:

   ```
   . /usr/lib/ckan/default/bin/activate
   ```

3. Clone the source and install it on the virtualenv

   ```
   git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git
   cd ckanext-dalrrd-emc-dcpr
   pip install -e .
   pip install -r requirements.txt
   ```

4. Add `dalrrd-emc-dcpr` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

5. Start CKAN:

   ```
   ckan -c /etc/ckan/default/ckan.ini run
   ```


## Development

It is strongly suggested that you use the provided `docker-compose.dev.yml`
file for development. It sets the following up:

- Bind mounts the code inside the relevant container(s) so that changes are
  instantly available inside them;

- Uses an automatically reloading web server, so that whenever the code
  changes, the server reloads too;

- Uses a common ckan configuration file with suitable settings for
  development - this file is located at `docker/ckan-dev-settings.ini`. It
  also includes the `docker/who.ini` file, which is another configuration
  file required by CKAN. The provided `ckan-dev-settings.ini`:

  - sets `debug = True`, which causes the ckan frontend to also load the
    [flask debug toolbar](https://flask-debugtoolbar.readthedocs.io/en/latest/)

- Exposes the following ports to the host machine:

  - ckan web: **5000**

  - ckan database: **55432**

  - datastore database: **55433**

  - solr: **8983**

- Uses docker named volumes for storing the ckan database, datastore database,
  ckan storage and solr data

- Makes it straightforward to run tests

Additionally, we suggest you use the provided `docker/compose.py` helper script
to stand up and wind down the stack.

```
cd docker

# bring the stack up
./compose.py up

# shut it down
./compose.py down

# restart services (for example the ckan-web service)
./compose.py restart ckan-web
```

After starting the stack, the ckan web interface is available (after a few
moments) on your local machine at

http://localhost:5000

**NOTE:** The compose file does not try to build the images. You either
build them yourself (with the provided `build.sh` script) or they are pulled
from the registry (if they exist remotely).


### First run

#### Initialize CKAN database

The first time you launch it you will need to set up the ckan database (since
the ckan image's entrypoint explicitly does not take care of this, as
mentioned above). Run the following command:

```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan db init
```

Now you should be able to go to `http://localhost:5000` and see the ckan
landing page. If not, you may need to reload the ckan web app after
performing the DB initialization step. This can done by sending the `HUP`
signal to the gunicorn application server (which is running our ckan
flask app):

```
docker exec -ti emc-dcpr_ckan-web_1 bash -c 'kill -HUP 1'
```


#### Create sysadmin user

After having initialized the database you can now create the first CKAN
sysadmin user.

```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan sysadmin add admin
```

Answer the prompts in order to provide the details for this new user.
After its successful creation you can login to the CKAN site with the `admin`
user.

### Bootstrap ckanext-harvest extension
The project uses the resource harvesting extension
to harvest and manage remote resources.

Run the following command to initialize the harvest database
```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan harvester initdb
```

If the above command runs successfully "DB tables created" message will be displayed
and the harvest source listing will be available under
http://localhost:5000/harvest

See https://github.com/ckan/ckanext-harvest for more ckanext-harvest extension backend configurations.

### Using CKAN commands

You can issue ckan commands inside the container by making sure they are run
with poetry. This can be done with `docker exec` oneliners like this:

```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan --help
```

Alternatively, you can open a bash shell inside the container use `poetry run`
there:

```
docker exec -ti emc-dcpr_ckan-web_1 bash

poetry run ckan --help
```

Lastly, you can open a bash shell, then open a poetry shell, which is
similar to activating its virtualenv, and then run commands, like this:

```
docker exec -ti emc-dcpr_ckan-web_1 bash

poetry shell

ckan --help
```



### Development in standalone (non-docker) mode

To install ckanext-dalrrd-emc-dcpr for development, activate your CKAN
virtualenv and do:

```
git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git
cd ckanext-dalrrd-emc-dcpr
python setup.py develop
pip install -r dev-requirements.txt
```


## Testing

To run the tests execute `pytest`:

    poetry run pytest --cov

This shall run the automated test suite and then print a coverage report
