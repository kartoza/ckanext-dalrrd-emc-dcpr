# A build script for the Dockerfile
#
# This script performs the following actions:
#
# - pull ancestor docker images in order to warm the build cache
# - perform the build
# - run automated smoke tests, to check if the image is not totally broken
# - push the generated image to the registry
#
# Built images are given duplicate tags:
#
# - one for the current git branch
# - the current git commit

set -euo pipefail

IMAGE_NAME=index.docker.io/kartoza/ckanext-dalrrd-emc-dcpr

GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD | tr / -)
GIT_COMMIT=$(git rev-parse --short HEAD)
DEFAULT_BRANCH=$(basename $(git rev-parse --abbrev-ref origin/HEAD) | tr / -)

# pull previous version, and use it with --cache-now, for build caching
docker pull $IMAGE_NAME:$DEFAULT_BRANCH || true
docker pull $IMAGE_NAME:$GIT_BRANCH || true

# use branch+commit for tagging
docker image build \
    -t "$IMAGE_NAME:$GIT_BRANCH" \
    -t "$IMAGE_NAME:$GIT_COMMIT" \
    --label git-commit=$GIT_COMMIT \
    --label git-branch=$GIT_BRANCH \
    --build-arg "BUILDKIT_INLINE_CACHE=1" \
    --build-arg "GIT_COMMIT=$GIT_COMMIT" \
    --cache-from=$IMAGE_NAME:$DEFAULT_BRANCH \
    --cache-from=$IMAGE_NAME:$GIT_BRANCH \
    ..

# run smoke tests
# python3 smoketest.py $IMAGE_NAME:$GIT_BRANCH

# push to docker registry
#docker push "$IMAGE_NAME:GIT_BRANCH"
#docker push "$IMAGE_NAME:GIT_COMMIT"
