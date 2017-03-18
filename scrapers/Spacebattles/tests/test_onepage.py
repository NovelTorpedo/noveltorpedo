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

from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
import time
import scrapy
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import sys
import os
import django
from reset_db import reset_database
from django.test import TestCase

sys.path.insert(0, "../../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from noveltorpedo.models import *


class SpaceBattlesTests():

    # do before each test...
    def __init__(self):
        self.settings = {}

    def setUp(self):
        self.settings = get_project_settings()
        self.settings["HTTPCACHE_ENABLED"] = 1
        self.settings["HTTPCACHE_EXPIRATION_SECS"] = 0
        self.settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
        self.settings["HTTPCACHE_IGNORE_MISSING"] = 1
        reset_database()

    def test_onepage(self):

        # The following value should be set to the test you want to run!
        self.settings["HTTPCACHE_DIR"] = "onepagetest"

        process = CrawlerRunner(self.settings)
        # runner = CrawlerRunner(self.settings)

        # print(settings)

        d = process.crawl('sb_spider')

        d.addBoth(lambda _: reactor.stop())
        # process.start()
        reactor.run()

        object_count = StorySegment.objects.count()

        if object_count == 5:
            print("PASS: Expected {0} story segments, received {1}".format(5, object_count))
            sys.exit(0)
        else:
            print("FAIL <test_onepage>: Expected {0} story segments, received {1}".format(5, object_count))
            sys.exit(1)

        # 5 is the expected number of entries in the table for this test.
        # exit status 1 if failed, 0 if success
        # self.assertEqual(object_count, 5)
        # time.sleep(5)

    def atest_twopage(self):

        # The following value should be set to the test you want to run!
        self.settings["HTTPCACHE_DIR"] = "twopagetest"

        process = CrawlerProcess(self.settings)

        # print(settings)

        process.crawl('sb_spider')
        # process.start(False)

        object_count = StorySegment.objects.count()
        # process.stop()
        # 5 is the expected number of entries in the table for this test.
        # exit status 1 if failed, 0 if success
        # self.assertEqual(object_count, 12)

if __name__=="__main__":
    test = SpaceBattlesTests()
    test.setUp()
    test.test_onepage()
