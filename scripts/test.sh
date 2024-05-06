#!/bin/bash

# Exit in case of error
set -e

# Force testing env config
export DEPLOYMENT_ENV=testing
# Disable DB initialization from JSON file
export INITIALIZE_DB=false

docker-compose build
docker-compose down -v --remove-orphans  # Remove possibly previous broken stacks left hanging after an error
docker-compose up -d
sleep 10
docker-compose exec -T backend bash /app/scripts/tests-start.sh "$@"

#docker-compose down -v --remove-orphans
