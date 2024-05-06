#!/bin/bash

# Exit in case of error
set -e

docker-compose build
docker-compose down -v --remove-orphans  # Remove possibly previous broken stacks left hanging after an error
docker-compose up -d
