#!/usr/bin/python

import os
import sys
sys.path.append('/var/www/pset')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pset.settings'

from django.core.management import setup_environ
from pset import settings
setup_environ(settings)

from main.models import *
from main.search_indexes import *
from haystack import connections

u = UserInfo.objects.filter(reindex=True, user__is_active=True)
index = connections['default'].get_unified_index().get_index(UserInfo)
connections["default"].get_backend().update(index,u)
u.update(reindex=False)
