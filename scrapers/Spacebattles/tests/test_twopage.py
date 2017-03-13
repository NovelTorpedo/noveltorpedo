from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.project import get_project_settings
import sys
import os
import time
import django
from reset_db import reset_database
from django.test import TestCase

sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from noveltorpedo.models import *


class TwoPageTests(TestCase):
    """
        Before you run the test, make sure httpcaching is enabled
        and IGNORE_MISSING is set to true.

        Make sure to run reset_db before running the test.
    """
    """
    def __init__(self, *args, **kwargs):
        super(TwoPageTests, self).__init__(*args, **kwargs)
        reset_database()

        self.settings = get_project_settings()
        self.settings["HTTPCACHE_ENABLED"] = 1
        self.settings["HTTPCACHE_EXPIRATION_SECS"] = 0
        self.settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
        self.settings["HTTPCACHE_IGNORE_MISSING"] = 1
        self.settings["HTTPCACHE_DIR"] = "twopagetest"

        process = CrawlerProcess(self.settings)

        # print(settings)

        process.crawl('sb_spider')
        process.start()
    """

    def setUp(self):
        """
            Place things that need to be reset between each
            test over here
        """

        self.settings = get_project_settings()
        self.settings["HTTPCACHE_ENABLED"] = 1
        self.settings["HTTPCACHE_EXPIRATION_SECS"] = 0
        self.settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
        self.settings["HTTPCACHE_IGNORE_MISSING"] = 1
        self.settings["HTTPCACHE_DIR"] = "twopagetest"

        reset_database()

    def atest_twopage(self):
        # The following value should be set to the test you want to run!
        # time.sleep(5)
        # process = CrawlerProcess(self.settings)
        process = CrawlerRunner(self.settings)

        d = process.crawl("sb_spider")
        d.addBoth(lambda _: reactor.stop())
        # process.start()
        reactor.run()

        object_count = StorySegment.objects.count()

        # 5 is the expected number of entries in the table for this test.
        # exit status 1 if failed, 0 if success
        self.assertEqual(object_count, 12,
                         "ERROR: expected {0} story segments, found {1}".format(12, object_count))
