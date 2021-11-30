#!/bin/sh
# In order to be sure that PostgreSQL has started
# and ready to accept connections.
if [ "$DATABASE_ENGINE" = "postgres" ]
then
    echo "Waiting for postgres on $..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"
