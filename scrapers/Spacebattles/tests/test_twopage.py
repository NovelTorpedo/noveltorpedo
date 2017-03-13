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


class TwoPageTests():
    """
        Before you run the test, make sure httpcaching is enabled
        and IGNORE_MISSING is set to true.

        Make sure to run reset_db before running the test.
    """

    def __init__(self):
        self.settings = {}
        self.expected_num_seg = 12

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

    def test_twopage(self):
        # The following value should be set to the test you want to run!
        # time.sleep(5)
        # process = CrawlerProcess(self.settings)
        process = CrawlerRunner(self.settings)

        d = process.crawl("sb_spider")
        d.addBoth(lambda _: reactor.stop())
        # process.start()
        reactor.run()

        object_count = StorySegment.objects.count()

        if object_count == self.expected_num_seg:
            print("PASS: Expected {0} story segments, received {1}".format(self.expected_num_seg,
                                                                           object_count))
            sys.exit(0)
        else:
            print("FAIL <test_onepage>: Expected {0} story segments, received {1}".format(self.expected_num_seg,
                                                                                          object_count))
            sys.exit(1)

if __name__=="__main__":
    test = TwoPageTests()
    test.setUp()
    test.test_twopage()