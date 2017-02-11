import scrapy
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


class StorySpider(scrapy.Spider):
    name = "sb_spider"
    priority = 1
    host = "spacebattles.com"

    thread_queue = []

    HOST, created = Host.objects.get_or_create(url="www.spacebattles.com", spider="sb_spider", wait=5)
    HOST.save()

    def start_requests(self):
        urls = [
            "https://forums.spacebattles.com/forums/creative-writing.18"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.loop_pages)

    def loop_pages(self, response):
            
        """ loop through the pages on the main page

        Keyword arguments:
        response -- the response object used to navigate the page

        """

        current_page = response.xpath("//a[@class='currentPage ']/text()")
        print("current page: {0}".format(current_page.extract_first()))

        next_page_link = response.xpath("//a[@class='text' and contains(., 'Next')]")
        next_page_link = next_page_link.xpath('@href').extract_first()

        # urls_stories is a tuple with a url, and a corresponding Story object
        urls_stories = self.get_thread_urls(response)

        for (url, story) in urls_stories:
            yield scrapy.Request(url, callback=self.scan_thread, priority=0, meta={"story_item": story})

        """
        if next_page_link is not None:

            #print("next page link: {0}".format(next_page_link))
            next_page_link = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_link, callback=self.loop_pages, priority=0)
        """

    def get_thread_urls(self, response):

        """ Scan the threads on a page

        Keyword arguments:
            response -- the response object used to navigate the page
        
        Return Value:
            ret      -- A list of urls to all threads on the page
        """

        print("scraping {0}".format(response.url))
        url_stories = []

        li_tags = response.xpath("//li[@class='discussionListItem visible  ']")

        for thread_tag in li_tags:

            author_name = thread_tag.xpath('@data-author').extract_first()
            author, created = Author.objects.get_or_create(name=author_name)

            author.save()

            title = thread_tag.xpath(".//h3[@class='title']/a/text()").extract_first().encode('utf-8')
            story, created = Story.objects.get_or_create(title=title)
            story.save()
            story.authors.add(author)

            a_node = thread_tag.xpath("div/div/h3/a")
            thread_url = a_node.xpath("@href").extract_first()

            cur_date = datetime.now(tz=utc)
            storyhost, created = StoryHost.objects.get_or_create(host=self.HOST,
                                                        story=story,
                                                        url=thread_url,
                                                        last_scraped=cur_date)

            storyhost.save()

            if thread_url is not None:

                thread_link = response.urljoin(thread_url)
                url_stories.append((thread_link, story))

        return url_stories

    def scan_thread(self, response):

        """ Scan the actual thread for story and author content

        This looks for any threadmarks, processes them, and
        follows the last threadmark's "next" link.
        If the page doesn't have any threadmarks, or there is
        no next link, it gracefully closes. It also creates story
        segments, and links them to a story. (django models)


        Keyword arguments:
        response -- the response object used to navigate the page

        META arguments:
            story_item -- the story object to associate the segments
        """
        story_item = response.meta.get("story_item")
        print("\nscraping thread {0}\n".format(response.url))

        div_tmarks = response.xpath("//li[contains(@class, 'hasThreadmark')]")
        
        if div_tmarks is not None and len(div_tmarks) > 0:

            for div_tmark in div_tmarks:
                story_seg = StorySegment()

                author = div_tmark.xpath("@data-author").extract_first()

                author_seg, created = Author.objects.get_or_create(name=author)
                story_item.authors.add(author_seg)

                title = "".join(div_tmark.xpath("div/span/text()").extract()).encode('utf-8')
                title = " ".join(title.split())
                story_seg.title = title
                story_seg.story = story_item

                # Get the Date and clean it up/format it ======================================
                date_time = div_tmark.xpath(".//span[@class='DateTime']/@title").extract_first()
                if date_time is None:
                    date_time = div_tmark.xpath(".//abbr[@class='DateTime']/text()").extract_first()
                date_obj = datetime.strptime(date_time, "%b %d, %Y at %I:%M %p")
                date_obj = date_obj.replace(tzinfo=utc)
                story_seg.published = date_obj
                # =============================================================================

                content = div_tmark.xpath(".//blockquote/text()").extract_first().encode('utf-8')
                content = " ".join(content.split())
                story_seg.contents = content

                print("Title: {0}   Author: {1}".format(story_seg.title, author))
                print("date_time: {0}".format(date_obj))
                # print("content: {0}".format(content[0:200]))

                story_seg.save()
                story_item.save()

            div_next_tmark = div_tmarks[-1].xpath(".//span[@class='next']")
            
            if div_next_tmark is not None:
                next_mark = div_next_tmark.xpath("a/@href").extract_first() 
                print("Next url: {0}".format(next_mark))
                next_mark_url = response.urljoin(next_mark)
                yield scrapy.Request(
                    next_mark_url,
                    callback=self.scan_thread,
                    priority=2,
                    meta={"story_item": story_item}
                )
