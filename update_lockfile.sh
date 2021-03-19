#!/bin/sh

# Run this after editing `requirements.txt` or `requirements-dev.txt`
# to freeze the latest depdencies to the lockfile used in production.

docker-compose build backend \
&& docker-compose run --rm backend sh -c '
    rm -rf ../.local/ \
    && pip install -r requirements.txt \
    && pip freeze --all > requirements.lock'
