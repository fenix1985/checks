#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "usage: $0 <message>"
    exit 1
fi

# disable DB initialization from JSON files
export INITIALIZE_DB=true

./scripts/rebuild.sh
# wait for DB tp start
sleep 15

tmpfile=$(mktemp -q /tmp/bar.XXXXXX)
# create a revision
docker-compose exec backend alembic revision --autogenerate -m "$1" | tee -a $tmpfile
# extract revision file name inside container
revision_file=$(tail -n 1 $tmpfile | sed 's/Generating \(.*\) ...  done/\1/' | tr -d '\r')
if [ ! -z "$revision_file" ]; then
    docker cp payment_app_backend_1:$revision_file alembic/versions/
fi
