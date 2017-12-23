#!/usr/bin/env bash

set -xeu

loc=$(cd $(dirname $0) && pwd)

docker exec gintest rm -rv /data/ssh
docker kill gintest

rm -r "${loc}/gin-data"
