"""A smoektest for newly built docker imges, to ensure basic correctness"""

import time
from subprocess import check_call
from urllib.request import urlopen

_CONTAINER_NAME = "smoketester"
_HOST_PORT = "8080"

check_call(f"docker run --rm --name={_CONTAINER_NAME} -p {_HOST_PORT}:80 -d httpd".split())


# Wait for server to start. A better implementation would use polling
time.sleep(5)

# Check if the server started
try:
    urlopen(f"http://localhost:{_HOST_PORT}").read()
finally:
    check_call(f"docker kill {_CONTAINER_NAME}".split())
