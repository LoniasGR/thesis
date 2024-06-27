#!/bin/bash

trap popd || true SIGINT

pushd app || true
uvicorn main:app --reload --port 8006 --host 0.0.0.0
