# emc-dcpr
Electronic Metadata Catalog for South Africa's Department of Agriculture, Land Reform and Rural Development

### Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.6 and earlier | not tested    |
| 2.7             | not tested    |
| 2.8             | not tested    |
| 2.9             | not tested    |


### Installation


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
