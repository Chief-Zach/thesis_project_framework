#!/bin/sh

if [ "$DEBUG" = 0 ]; then
  echo "RUNNING IN PRODUCTION MODE"
  exec gunicorn --workers 1 --bind 0.0.0.0:8000 -m 777 -k uvicorn.workers.UvicornWorker "wsgi:app_factory()"
else
  echo "RUNNING IN DEBUG MODE"
  exec uvicorn wsgi:app_factory --host 0.0.0.0 --port 8000 --factory --reload

fi
