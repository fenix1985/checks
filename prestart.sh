#! /usr/bin/env bash

export INITIALIZE_ALEMBIC

# Let the DB start
# running in docker container
python /app/scripts/backend_pre_start.py

# Run migrations
if [ "$INITIALIZE_ALEMBIC" = true ]
then
    alembic upgrade head
fi

# Insert init data
#python /app/scripts/backend_init_data.py
