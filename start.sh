#!/bin/sh
while ! pg_isready -h $DJANGO_DATABASE_HOST -p "5432" > /dev/null 2> /dev/null; do
   echo "Waiting for DB host....."
   sleep 1
done
echo "Collecting static files"
python3 manage.py collectstatic --noinput
echo "Migrating DB"
python3 manage.py migrate --noinput
echo "Starting uwsgi server"
uwsgi uwsgi.ini
