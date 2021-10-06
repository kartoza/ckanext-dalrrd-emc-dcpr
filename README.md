# ckanext-dalrrd-emc-dcpr

This is a [ckan](https://ckan.org) extension that implements the Electronic Metadata Catalog for 
South Africa's Department of Agriculture, Land Reform and Rural Development. It also contains
additional utilities, useful for running the full EMC.

## Installation

While this project can be installed standalone, it is primarily meant to be used together with docker


### docker standalone installation

- Pull the latest release (not the `latest` tag) of the project from the docker registry:

  ```
  docker pull kartoza/ckanext-dalrrd-emc-dcpr
  ```
  
  Alternatively, you can also build the image locally by using the provided build script:

  ```
  cd docker
  ./build.sh
  ```
  
- Use the docker image by providing a volume that has your desired CKAN configuration file. In order to be 
  properly recognized, your config file must be mounted at `/home/appuser/app/ckan.ini`. For example, 
  when running standalone:

  ```
  docker run --rm --name mytester --volume=/home/myuser/my-ckan.ini:/home/appuser/app/ckan.ini
  ```
  

The provided `Dockerfile` has the following peculiarities:

- It **requires** you to mount the ckan configuration file in order to work
- Uses [poetry](https://python-poetry.org/) to install Python packages and manage their environment
- A custom docker entrypoint script implemented in Python. It has access to the poetry env and can 
  be called by running `poetry run docker_entrypoint`
- Uses [gunicorn](https://gunicorn.org/) as the Python app server.

  
## Development

It is suggested that you use the provided `docker-compose.dev.yml` file for development. It sets the following up:

- Bind mounts the code inside the relevant container(s) so that changes are instantly available inside them;
- Uses an automatically reloading web server, so that whenever the code changes the server reloads
- Uses a common ckan configuration file with suitable settings for development
- Makes it straightforward to run tests

```
cd docker
docker-compose --project-name=emc-dcpr --file docker-compose.dev.yml up --detach
```


### Setting up

you can run the main image as a standalone container, when setting up

```
cd docker
docker run --rm --name tester -ti --volume $PWD/..:/home/appuser/app --volume $PWD/ckan-dev-settings.ini:/home/appuser/ckan.ini --entrypoint=/bin/bash kartoza/ckanext-dalrrd-emc-dcpr:add-dockerfile
```
  

## Installation


To install ckanext-dalrrd-emc-dcpr, make sure CKAN is already installed on your virtual environment
if not follow the https://docs.ckan.org/en/2.9/maintaining/installing/install-from-source.html guide to install CKAN,
then follow the below steps:

1. Activate your CKAN virtual environment, for example:

     `. /usr/lib/ckan/default/bin/activate`

2. Clone the source and install it on the virtualenv

    `git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git` \
    `cd ckanext-dalrrd-emc-dcpr` \
    `pip install -e .` \
    `pip install -r requirements.txt `

3. Add `dalrrd-emc-dcpr` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Start CKAN:

     `ckan -c /etc/ckan/default/ckan.ini run`


### Developer installation

To install ckanext-dalrrd-emc-dcpr for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/Kartoza/ckanext-dalrrd-emc-dcpr.git
    cd ckanext-dalrrd-emc-dcpr
    python setup.py develop
    pip install -r dev-requirements.txt


### Tests

To run the tests, do:

    pytest --ckan-ini=test.ini
