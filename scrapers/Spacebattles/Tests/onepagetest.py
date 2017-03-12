from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os
import django
from reset_db import reset_database


sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from noveltorpedo.models import *


def run_test():
    # reset the database before you run the test
    reset_database()

    """
        Before you run the test, make sure httpcaching is enabled
        and IGNORE_MISSING is set to true.
    """
    settings = get_project_settings()
    settings["HTTPCACHE_ENABLED"] = 1
    settings["HTTPCACHE_EXPIRATION_SECS"] = 0
    settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
    settings["HTTPCACHE_IGNORE_MISSING"] = 1

    # The following value should be set to the test you want to run!
    settings["HTTPCACHE_DIR"] = "onepagetest"

    process = CrawlerProcess(settings)

    # print(settings)

    process.crawl('sb_spider')
    process.start()

    object_count = StorySegment.objects.count()

    # 5 is the expected number of entries in the table for this test.
    # exit status 1 if failed, 0 if success
    if object_count is not 5:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    run_test()