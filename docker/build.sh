set -euo pipefail

IMAGE_NAME=index.docker.io/kartoza/ckanext-dalrrd-emc-dcpr

GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT=$(git rev-parse --short HEAD)
DEFAULT_BRANCH=$(basename $(git rev-parse --abbrev-ref origin/HEAD))

# pull previous version, and use it with --cache-now, for build caching
docker pull $IMAGE_NAME:$DEFAULT_BRANCH || true
docker pull $IMAGE_NAME:$GIT_BRANCH || true

# use branch+commit for tagging
docker image build \
    -t "$IMAGE_NAME:$GIT_BRANCH" \
    -t "$IMAGE_NAME:$GIT_COMMIT" \
    --label git-commit=$GIT_COMMIT \
    --label git-branch=$GIT_BRANCH \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg git-commit=$GIT_COMMIT \
    --cache-from=$IMAGE_NAME:$DEFAULT_BRANCH \
    --cache-from=$IMAGE_NAME:$GIT_BRANCH \
    ..

# run smoke tests
python smoketest.py $IMAGE_NAME:$GIT_BRANCH

# push to docker registry
#docker push "$IMAGE_NAME:GIT_BRANCH"
#docker push "$IMAGE_NAME:GIT_COMMIT"
