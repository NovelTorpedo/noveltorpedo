# Copyright 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu, Rubin Stricklin, and Sage Callon
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

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


