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
from datetime import datetime
import time
from datetime import timedelta

from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import sys
import os
import django

sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def continue_crawl(d, runner, begin_time, hour_limit):
    """
    Continues the crawler process.

    :param d:
    :param runner:
    :param begin_time
    :param hour_limit
    :return:
    """
    end_time = datetime.now()

    # Convert elapsed time to seconds
    elapsed_time = end_time - begin_time
    elapsed_time_seconds = elapsed_time.days * 86400
    elapsed_time_seconds += elapsed_time.seconds

    print("Total time elapsed: {0}".format(elapsed_time_seconds))
    if elapsed_time_seconds < hour_limit:
        wait_time = hour_limit - elapsed_time_seconds
        print("Waiting for {0} seconds".format(wait_time))
        time.sleep(wait_time)

    d = runner.crawl("sb_spider")

    # end_time is the new "start" time for this iteration of the spider.
    # Pass it in as the 3rd argument.
    d.addBoth(lambda _: continue_crawl(d, runner, end_time, hour_limit))

def run_spiders():
    """
        Initialize a crawler, and start reactor. Loop
        the crawler with the deferred return type.

    :return:
    """
    hour_limit = 3600  # in seconds

    settings = get_project_settings()

    settings["HTTPCACHE_ENABLED"] = 1
    settings["HTTPCACHE_EXPIRATION_SECS"] = 0
    settings["HTTPCACHE_STORAGE"] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
    settings["HTTPCACHE_IGNORE_MISSING"] = 1
    settings["HTTPCACHE_DIR"] = "onepagetest"

    runner = CrawlerRunner(settings)
    begin_time = datetime.now()

    d = runner.crawl("sb_spider")
    d.addBoth(lambda _: continue_crawl(d, runner, begin_time, hour_limit))
    reactor.run()

if __name__ == "__main__":
    run_spiders()
