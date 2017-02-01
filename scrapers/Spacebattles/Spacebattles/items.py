# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StorySegment(scrapy.Item):
    # define the fields for your item here like:
    #  = scrapy.Field()
    content = scrapy.Field()
    nsfw_flag = scrapy.Field()
    next_url = scrapy.Field()


class Story(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    # nsfw_flag = scrapy.Field()
    url = scrapy.Field()
    segments = []
