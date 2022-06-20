# ckanext-dalrrd-emc-dcpr

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/kartoza/ckanext-dalrrd-emc-dcpr/Local%20CI/main)
![Docker Image Version (latest by date)](https://img.shields.io/docker/v/kartoza/ckanext-dalrrd-emc-dcpr)

This is a [ckan](https://ckan.org) extension that implements the Electronic
Metadata Catalog for South Africa's Department of Agriculture, Land Reform
and Rural Development (DALRRD). It also contains additional utilities,
useful for running the full EMC.


## Dataset metadata fields

Dataset fields are defined with the help of the [ckan scheming extension](https://github.com/ckan/ckanext-scheming).
The dataset schema file can be found in `ckanext/dalrrd_emc_dcpr/scheming/dataset_schema.yaml`. It has the definition
of the EMC dataset metadata fields, which conform with the South African spatial metadata standard (SANS1878)


## Deployment

This project is deployed onto the following environments:

- **testing :orange_circle:** - https://testing.emc.kartoza.com
- **staging**: TBD
- **production**: TBD

Deployment details are kept elsewhere.


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

2. Clone the source and install it on the virtualenv

   ```
   git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git
   cd ckanext-dalrrd-emc-dcpr
   pip install -e .
   pip install -r requirements.txt
   ```

3. Add `dalrrd-emc-dcpr` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Start CKAN:

   ```
   ckan -c /etc/ckan/default/ckan.ini run
   ```


## Migrations

Run the extension's specific migrations using the following commands to upgrade and downgrade
the ckan database respectively.

```
docker exec -t emc-dcpr_ckan-web_1 poetry run ckan db upgrade -p dalrrd_emc_dcpr
docker exec -t emc-dcpr_ckan-web_1 poetry run ckan db downgrade -p dalrrd_emc_dcpr
``````


## Operations

#### Rebuild solr index

```
# check if there are any datasets that are not indexed
ckan search-index check

# re-index
ckan search-index rebuild
```


#### Update extents of spatial datasets

```
ckan spatial extents
```


#### Create bootstrap items

```
ckan dalrrd-emc-dcpr bootstrap create-sasdi-themes
ckan dalrrd-emc-dcpr bootstrap create-iso-topic-categories
ckan dalrrd-emc-dcpr bootstrap create-sasdi-organizations
```


#### Update page view tracking

This needs to be run periodically (once per day is enough). Be sure to run both commands depicted below.

```
ckan tracking update
ckan search-index rebuild --refresh
```


#### Operate harvesters

You may use the various `ckan harvester <command>` commands to operate existing
harvesters

Create a job:

```
docker exec -ti emc_dcpr-ckan_harvesting-runner poetry run ckan harvester job <source-id>
```


#### Send notifications by email

This needs to be run periodically (once per hour is likely enough).

```
ckan dalrrd-emc-dcpr send-email-notifications
```

Additionally, in order for notifications to work, there is some configuration:

- The CKAN settings must have `ckan.activity_streams_email_notifications = true`
- The CKAN settings must have the relevant email configuration (likely being passed
  as environment variables)
- Each user must manually choose to receive notification e-mails - This is done in
  the user's profile
- Each user must manually follow those entities (datasets, organizations, etc) that
  it finds interesting enough in order to be notified of changes via email


#### Use a shell for interacting with CKAN

There is a CLI command that allows opening a Python shell already configured with the
CKAN environment. This is analogous to django's `manage.py shell` command. Start it up with:

```
ckan shell
```


#### Refresh pycsw materialized view

This needs to be run periodically (once per hour is likely enough).

```
ckan dalrrd-emc-dcpr pycsw refresh-materialized-view
```


## Development

It is strongly suggested that you use the provided docker-compose related
files for development. They set the following up:

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
./compose.py --compose-file docker-compose.yml --compose-file docker-compose.dev.yml up

# shut it down
./compose.py --compose-file docker-compose.yml --compose-file docker-compose.dev.yml down

# restart services (for example the ckan-web service)
./compose.py --compose-file docker-compose.yml --compose-file docker-compose.dev.yml restart ckan-web
```

After starting the stack, the ckan web interface is available (after a few
moments) on your local machine at

http://localhost:5000

**NOTE:** The compose file does not try to build the images. You either
build them yourself (with the provided `build.sh` script, as mentioned above) or they are pulled
from the registry (if they exist remotely).


### First run

#### Initialize CKAN database

The first time you launch it you will need to set up the ckan database (since
the ckan image's entrypoint explicitly does not take care of this, as
mentioned above). Run the following command:

```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan db init
```

Afterwards, proceed to run any migrations required by the ckanext-dlarrd-emc-dcpr extension

```
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan db upgrade --plugin dalrrd_emc_dcpr
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


#### Setup datastore db

The datastore DB requires the creation of a readonly user. The commands to do this are sent directly to
the `datastore-db` service by means of mounting a custom script inside the
container's `/docker-entrypoint-initdb.d` directory. This means that the DB is initialized automatically
when the container is created.


##### NOTE

As mentioned in the [postgres docker docs](https://hub.docker.com/_/postgres), the DB initialization
script is only ran if the container's data directory is empty. This means that if there is already
a pre-existing DB, the script will not be executed. If needed, remove the volume that has the DB's
data directory and then initialize the container again - THIS WILL TRASH YOUR DB!

```
docker volume rm emc-dcpr_datastore-db-data
```


#### Bootstrap additional CKAN extensions

Run the following command in order to have additional extensions correctly get their
DB tables created:

```bash
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan spatial initdb
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan harvester initdb
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan pages initdb
```


##### NOTES

The ckanext-spatial extension takes care of its own bootstrapping and will create any database tables
automatically. However, you may want to bootstrap explicitly. If so, run:

```bash
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan spatial initdb
```

Additionally, the spatial extension documentation seems to be outdated when it comes to
running its custom CKAN CLI commands. Instead
of the older `paster`-based incantation, they should rather be ran like:

```sh
poetry run ckan spatial <command>
```


#### Generate pycsw DB view

In order to be able to serve the system's datasets through various OGC standards, create a DB materialized view
in order to integrate with pycsw:

```bash
docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan dalrrd-emc-dcpr pycsw create-materialized-view
```


### Bootstrap the system

Create the default items required by the EMC/DCPR system by running the
bootstrap commands as described in the [Operations section](#operations)


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


### Recreating the main CKAN DB

The CKAN database is kept in a docker volume named `emc-dcpr_ckan-db-data`. If you need to recreate the DB you
can remove this docker volume. Do the following:

- If needed, wind down the docker-compose stack;
- Remove the DB volume with `docker volume rm emc-dcpr_ckan-db-data`
- Start the docker-compose stack again
- Run the DB initialization command
- Bootstrap the system again


### Frontend work

#### CSS

##### Less files

CKAN, the base of the SASDI EMC stack, uses [bootstrap version 3.4.1](https://getbootstrap.com/docs/3.4/). The main
CSS file is generated with [Less](https://lesscss.org/) and what is distributed are the compiled `.css` files.

In order to hook into those Less files and have an easier way to define global variables and styles we need to install
some additional dependencies and set up a CSS building pipeline.

This is done by following the steps below:

- Start the docker-compose stack with the development files
- Run the provided `docker/prepare-for-frontend-dev.sh` script. This will install [node.js](https://nodejs.org/en/)
  inside the running container, then use npm to install the dependencies mentioned in the `package.json` file and
  immediately start watching for changes:

  ```bash
  docker exec -ti emc-dcpr_ckan-web_1 bash docker/prepare-for-frontent-dev.sh
  ```

- Now you may edit the `public/base/less` files and reload your web browser to see the changes


#### Vanilla CSS files

The `assets/css/dalrrd-emc-dcpr.css` file can be used to write custom CSS directly. Editing this
file can be done when the changes do not involve modifying Less variables - it also does not require nodejs to be
installed


### Continuous Integration and git pre-commit

This project uses a Continuous Integration strategy whereby each commit (either to `main` or via some PR)
is checked by an automated github workflow. This performs several checks:

- Lint the code with [black](https://black.readthedocs.io/en/stable/)
- Perform static analysis by running the code through [mypy](http://mypy-lang.org/)
- Build the docker image
- Run automated tests

Generally, in order for a PR to be accepted it must pass these automated checks.

In order to avoid waiting around for the pipeline to find issues, it is advisable to install
[pre-commit](https://pre-commit.com/) and use the provided `.pre-commit-config.yaml` file to ensure that
at least the linting and static analysis checks are run as git pre-commit hooks. It is also advisable to run
the tests locally, before pushing your changes to github (see the next section for instructions on running tests).

This project also uses a Continuous Deployment pipeline where each commit to the `main` branch results in
the redeployment of our testing environment.


### Development in standalone (non-docker) mode

To install ckanext-dalrrd-emc-dcpr for development, activate your CKAN
virtualenv and do:

```
git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git
cd ckanext-dalrrd-emc-dcpr
python setup.py develop
pip install -r dev-requirements.txt
```


### Testing

Testing uses some additional configuration:

- The `docker/docker-compose.dev.yml` file has an additional `ckan-tests-db` service, with a DB that is uses solely
  for automated testing.
- The  `docker/ckan-test-settings.ini` file defines the test settings. It must be explicitly passed as the config
  file to use when running the tests

To run the tests you will need to:

1. Install the development dependencies beforehand, as the docker images do not have them. Run:

   ```
   docker exec -ti {container-name} poetry install
   ```

2. Initialize the db - this is only needed the first time (the dev stack uses volumes to persist the DB)

   ```
   docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan --config docker/ckan-test-settings.ini db init
   docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan --config docker/ckan-test-settings.ini harvester initdb
   docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan --config docker/ckan-test-settings.ini db upgrade -p dalrrd_emc_dcpr
   ```

3. When there are model changes you will need to upgrade the DB too. Run this:

   ```
   docker exec -ti emc-dcpr_ckan-web_1 poetry run ckan --config docker/ckan-test-settings.ini db upgrade -p dalrrd_emc_dcpr
   ```

4. Run the tests with `pytest`. We use markers to differentiate between unit and integration tests. Run them like this:

   ```
   # run all tests
   poetry run pytest --ckan-ini docker/ckan-test-settings.ini

   # run only unit tests
   poetry run pytest --ckan-ini docker/ckan-test-settings.ini -m unit

   # run only integration tests
   poetry run pytest --ckan-ini docker/ckan-test-settings.ini -m integration
   ```


## Harvesting

- Using [httpie](https://httpie.io/) to check for existing records on the local pycsw test service:

  ```
  http localhost:55436 \
      service==CSW \
      version==2.0.2 \
      request==GetRecords \
      resulttype==results \
      typenames=gmd:MD_Metadata \
      outputschema==http://www.isotc211.org/2005/gmd \
      elementsetname==brief
  ```

- Create a CKAN harvester for the local docker-based pycsw service:

  - URL: `http://csw-harvest-target:8000`
  - Source type: `CSW Server`
  - Update frequency: `Manual`
  - Configuration: `{"default_tags": ["csw", "harvest"]}`
  - Organization: `test-org-1`

## Kubernetes Pod Shell

To run any of the above docker commands once this is deployed into Kubernetes you can use one of 3 ways:

1. By accessing Rancher:
  1. Go to Rancher2 > Shared (in header bar) > EMC-DCPR
  2. Go to the "ckan" Workload
  3. On a running pod click on the menu and select "Execute Shell"
2. By Using Lens:
  1. Go to Workloads > Deployments.
  2. Choose the correct namespace: "emc-dcpr"
  3. Select the Deployment "ckan"
  4. Scroll to Pods
  5. Select a running one
  6. Click on "Pod Shell".
3. Using the Kubernetes CLI
  1. Get the pod name: `kubectl get pods --namespace=emc-dcpr`, it should look like `ckan-<randon string>`
  2. Run `kubectl exec -it <pod name> --namespace=emc-dcpr -- bash`
  3. Or an all in one: `kubectl exec -it "$(kubectl get pods --namespace=emc-dcpr | grep Running | grep ckan- | grep -v postgis | cut -d' ' -f1)" --namespace=emc-dcpr -- bash`


## User feedback

The system is using the [crisp] chatbox to allow gathering feedback from users. Configure it at the crisp website

[crisp]: https://crisp.chat/en/


## Import of legacy SASDI EMC datasets

There is some support for importing legacy SASDI EMC datasets. For now, it is available in the form of additional CLI
commands:

- `ckan legacy-sasdi saeon-odp import-records` - These commands use the legacy SASDI EMC SAEON-ODP platform and rely
  on the records being in the DataCITE format. For now there is no provision for downloading records from some remote
  server

- `ckan legacy-sasdi csw <command>` - These commands use the legacy SASDI EMC CSW endpoint and retrieve records via CSW
  - `ckan legacy-sasdi csw dowload-records`
  - `ckan legacy-sasdi csw import-records`
  - `ckan legacy-sasdi csw retrieve-thumbnails`
