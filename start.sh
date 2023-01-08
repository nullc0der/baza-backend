#!/bin/sh
while ! pg_isready -h $DJANGO_DATABASE_HOST -p "5432" > /dev/null 2> /dev/null; do
   echo "Waiting for DB host....."
   sleep 1
done
echo "Collecting static files"
python manage.py collectstatic --noinput
echo "Migrating DB"
python manage.py migrate --noinput
# TODO: add circus here and serve both wsgi and asgi seperately when app grows
# Another approach, you can setup two different container for asgi and wsgi
echo "Starting ASGI server"
daphne -b 0.0.0.0 -p 8000 -v 1 --access-log /dev/stdout bazaback.asgi:application
