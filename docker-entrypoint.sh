#!/bin/sh

cd /code

flask db init
flask db migrate
flask db upgrade

python manage.py run