#!/bin/sh

python manage.py makemigrations
python manage.py migrate

./wait-for-it.sh db:5432 -- python manage.py runserver 0.0.0.0:8081