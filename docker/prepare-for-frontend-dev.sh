# A script for setting up the environment for frontend work

# unfortunately we cannot set -eu due to a bug with nvm:
#    https://github.com/nvm-sh/nvm/issues/1526
# set -euo pipefail

_PYTHON_VERSION=$(echo $(poetry run python --version | cut -f 2 -d ' ') | cut -f 1-2 -d '.')
_CKAN_INSTALL_PATH=$(poetry env info -p)/lib/python${_PYTHON_VERSION}/site-packages/ckan

# copy over the relevant dirs to a known-location
mkdir --parents ~/ckan-frontend
cp --recursive ${_CKAN_INSTALL_PATH}/public/base/vendor ~/ckan-frontend
cp --recursive ${_CKAN_INSTALL_PATH}/public/base/less ~/ckan-frontend

# install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# install node version 13, which is what ckan is using
nvm install v13

# install ckan frontend dependencies, as specified in the `package.json` file
npm install

npm run docker-watch
