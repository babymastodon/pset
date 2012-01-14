#!/bin/bash

cd documents
compass compile 
compass compile --output-style compressed --css-dir custom_static --force
cd ..
./manage.py collectstatic --noinput
./manage.py syncdb
touch ./${PWD##*/}/wsgi.py
