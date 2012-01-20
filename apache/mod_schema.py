#!/usr/bin/python

import os, re
filepath = os.path.join(os.path.dirname(__file__),'solr_schema.xml')
schemafile = open(filepath,'r')
contents = schemafile.read()
schemafile.close()
contents = re.sub("""<field name="subcategories" type="text.{0,10}" indexed="true" stored="true" multiValued="true" />""","""<field name="subcategories" type="string" indexed="true" stored="true" multiValued="true" />""", contents)
contents = re.sub("""<field name="categories" type="text.{0,10}" indexed="true" stored="true" multiValued="true" />""","""<field name="categories" type="string" indexed="true" stored="true" multiValued="true" />""", contents)
outfile = open(filepath,'w')
outfile.write(contents)
outfile.close()
