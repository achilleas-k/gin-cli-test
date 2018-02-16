#!/usr/bin/env bash

set -eu

loc=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
pushd $loc

docker build --build-arg UID=${UID} dockerfiles/tester

source ./scripts/setenv.sh
mkdir -p ${GIN_LOG_DIR}
testlog=${GIN_LOG_DIR}/tests.log
echo "Running tests and logging to ${testlog}"
docker run --rm --network=ginbridge -v "${loc}/testuserhome":/home/ginuser -v "${loc}/scripts/":/home/ginuser/scripts -v "${loc}/bin/":/ginbin --name gintestclient ginclitests &> ${testlog}
