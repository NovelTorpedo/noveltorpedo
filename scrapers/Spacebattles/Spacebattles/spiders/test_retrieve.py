import scrapy
import time
import sys
import os
from django.conf import settings
from django.db import connection
import django


sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# setup_environ(settings)
django.setup()

from noveltorpedo.models import *


class RetrieveSpider(scrapy.Spider):
    name = "retrieve_test"


    def start_requests(self):
        urls = [
            "https://forums.spacebattles.com/forums/creative-writing.18"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.retrieve_test)


    def retrieve_test(self, response):
        stories = Story.objects.all()
        print(stories)
