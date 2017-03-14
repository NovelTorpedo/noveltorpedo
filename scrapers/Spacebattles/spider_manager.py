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

from scrapy.crawler import CrawlerRunner
import time
import scrapy
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import sys
import os
import django
from django.test import TestCase
from tests.reset_db import reset_database

sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def continue_crawl(d, runner):
    """
    Continues the crawler process.

    :param d:
    :param runner:
    :return:
    """
    # maybe put a time.sleep call here?

    d = runner.crawl("sb_spider")

    d.addBoth(lambda _: continue_crawl(d, runner))

def run_spiders():
    """
        Initialize a crawler, and start reactor. Loop
        the crawler with the deferred return type.

    :return:
    """
    settings = get_project_settings()
    """
    settings["HTTPCACHE_ENABLED"] = 1
    settings["HTTPCACHE_EXPIRATION_SECS"] = 0
    settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
    settings["HTTPCACHE_IGNORE_MISSING"] = 1
    settings["HTTPCACHE_DIR"] = "onepagetest"
    """
    runner = CrawlerRunner(settings)

    d = runner.crawl("sb_spider")
    d.addBoth(lambda _: continue_crawl(d, runner))
    reactor.run()

if __name__ == "__main__":
    run_spiders()
