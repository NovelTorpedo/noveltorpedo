from datetime import datetime
import sys
import os
import re
from pytz import utc
from django.conf import settings
from django.db import connection
import django


sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# setup_environ(settings)
django.setup()

from noveltorpedo.models import *

cursor = connection.cursor()
cursor.execute('TRUNCATE TABLE noveltorpedo_story CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_story_authors CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_story_segments CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_story_hosts CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_author CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_story CASCADE')


