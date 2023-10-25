#!/bin/bash

set -e

USID=$(id -u)
GID=$(id -g)

export USID
export GID

pushd ./frontend
npm run build
popd

docker compose build

touch sql_app.db
docker compose up -d
