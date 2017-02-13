from django import template
from config.settings import STATICFILES_DIRS
import os
# import re

"""
Adapted from:

https://muffinresearch.co.uk/automatic-asset-versioning-in-django/
"""

register = template.Library()

STATIC_PATH = STATICFILES_DIRS[0]
version_cache = {}

# rx = re.compile(r"^(.*)\.(.*?)$")


def version(path_string):
    try:
        if path_string in version_cache:
            mtime = version_cache[path_string]
        else:
            mtime = os.path.getmtime(os.path.join(STATIC_PATH, path_string))
            version_cache[path_string] = mtime

        # return rx.sub(r"\1.%d.\2" % mtime, path_string)
        return '/static/' + path_string + "?v=" + str(int(mtime))
    except:
        return '/static/' + path_string

register.simple_tag(version)
