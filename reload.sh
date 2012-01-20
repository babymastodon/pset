#!/bin/bash

cd documents
compass compile 
compass compile --output-style compressed --css-dir custom_static --force
cd ..
./manage.py collectstatic --noinput
./manage.py syncdb
./manage.py build_solr_schema > apache/solr_schema.xml
python apache/mod_schema.py
touch ./${PWD##*/}/wsgi.py
