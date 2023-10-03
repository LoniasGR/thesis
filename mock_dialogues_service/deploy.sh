#!/bin/bash

pushd ./frontend || exit
npm run build
popd || exit

docker compose build
docker compose up -d
