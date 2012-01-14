import os
import sys
FILENAME = os.path.dirname(os.path.realpath(__file__))
SITE_ROOT = os.path.normpath(os.path.join(FILENAME,'..'))
if SITE_ROOT not in sys.path:
    sys.path.append(SITE_ROOT)

os.environ['DJANGO_SETTINGS_MODULE'] = os.path.split(SITE_ROOT)[1] + '.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
