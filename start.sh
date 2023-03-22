#!/bin/bash

#cron

cd /app

python3 manage.py collectstatic --noinput && \
python3 manage.py migrate && \
python3 manage.py initial_system && \
#gunicorn -w $GUNICORN_WORKER_NO --bind :$GUNICORN_LISTENINIG_PORT --timeout $GUNICORN_TIMEOUT its.wsgi
python3 manage.py runserver 0.0.0.0:$GUNICORN_LISTENINIG_PORT