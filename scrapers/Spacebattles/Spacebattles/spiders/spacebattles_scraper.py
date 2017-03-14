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

    # these variables are used to generate testing situations
    generate_test = None
    test_url = None
    custom_settings = {
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "HTTPCACHE_STORAGE": 'scrapy.extensions.httpcache.FilesystemCacheStorage',
        "HTTPCACHE_ENABLED": 1,
        "HTTPCACHE_DIR": "twopagetest",
        "HTTPCACHE_IGNORE_MISSING": 1
    }

    # this will be a list of tuples (of story objects and urls)
    update_list = []

    # try to get the host object for this Host. Create if not found.
    HOST, created = Host.objects.get_or_create(url="www.spacebattles.com", spider="sb_spider", wait=5)
    HOST.save()

    def __init__(self, generate_test=None, test_url=None, *args, **kwargs):
        super(StorySpider, self).__init__(*args, **kwargs)
        self.generate_test = generate_test
        self.test_url = test_url

    def start_requests(self):
        urls = [
            "https://forums.spacebattles.com/forums/creative-writing.18"
        ]

        # start the requests for the base urls. Currently only scraping
        # creative-writing.18
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

        if self.generate_test is None:
            # generate requests for -- new -- stories
            for (url, story) in urls_stories:
                yield scrapy.Request(url, callback=self.scan_thread, priority=1, meta={"story_item": story})

            # generate requests for stories that need to be updated.
            for (url, story) in self.update_list:
                yield scrapy.Request(url, callback=self.update_stories, priority=2, meta={"story_item": story})

            if next_page_link is not None:

                # print("next page link: {0}".format(next_page_link))
                next_page_link = response.urljoin(next_page_link)
                yield scrapy.Request(next_page_link, callback=self.loop_pages, priority=0)
        else:
            """
                This section activates if self.generate_test is not None.
                A thread url is required to be provided to generate a test scenario out of that
                thread.
                It scans the site looking for this thread, and scrapes it.
                If it doesn't find it, it scans the next page.
            """
            print("\n\tGENERATING TEST SCENARIO\n")
            for (url, story) in urls_stories:
                if url == self.test_url:
                    yield scrapy.Request(url, callback=self.scan_thread, priority=0, meta={"story_item": story})
                    return

            for (url, story) in self.update_list:
                if url == self.test_url:
                    yield scrapy.Request(url, callback=self.scan_thread, priority=0, meta={"story_item": story})
                    return

            next_page_link = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_link, callback=self.loop_pages, priority=0)

    def get_thread_urls(self, response):

        """ Scan the threads on a page

        Keyword arguments:
            response -- the response object used to navigate the page
        
        Return Value:
            ret      -- A list of urls to all threads on the page
        """

        print("scraping {0}".format(response.url))
        url_stories = []

        # <li_tags> is a list of all the <li> tags in the html doc with a certain class value.
        # This corresponds to all threads that are NOT sticky.
        li_tags = response.xpath("//li[@class='discussionListItem visible  ']")

        for thread_tag in li_tags:

            author_name = thread_tag.xpath('@data-author').extract_first()

            # Get the last post date for a thread ========================================================
            last_post_date = thread_tag.xpath(".//dl[@class='lastPostInfo']//abbr/text()").extract_first()
            if last_post_date is not None:
                last_post_date = datetime.strptime(last_post_date, "%b %d, %Y at %I:%M %p").replace(tzinfo=utc)
            else:
                # fix with line continuation.
                last_post_date = thread_tag.xpath(".//span[@class='DateTime']/@title").extract_first()
                last_post_date = datetime.strptime(last_post_date, "%b %d, %Y at %I:%M %p").replace(tzinfo=utc)

            # ============================================================================================

            author, created = Author.objects.get_or_create(name=author_name)
            if created:
                author.save()

            title = thread_tag.xpath(".//h3[@class='title']/a/text()").extract_first().encode('utf-8')
            story, created = Story.objects.get_or_create(title=title)

            # if created is true, then it's a brand new story, so make sure to save it.
            if created:
                story.save()
            story.authors.add(author)

            a_node = thread_tag.xpath("div/div/h3/a")
            thread_url = a_node.xpath("@href").extract_first()

            cur_date = datetime.now(tz=utc)
            oldest_date = datetime.min.replace(tzinfo=utc)

            created = False
            """
                Over here, I am attempting to either update an existing storyhost
                object, OR I am creating a new one. It looks redundant, but I found that
                if I just used get_or_create, I was forced to set last_date automatically.

                I didn't always want to create a brand new object, so this verbose code
                was necessary.
            """
            try:
                # TRY TO UPDATE EXISTING object
                storyhost = StoryHost.objects.get(host=self.HOST, story=story, url=thread_url)
                storyhost.save()
            except StoryHost.DoesNotExist:

                # CREATE BRAND NEW STORYHOST OBJECT
                storyhost, created = StoryHost.objects.get_or_create(host=self.HOST,
                                                                     story=story,
                                                                     url=thread_url,
                                                                     last_scraped=oldest_date)

                storyhost.save()

            """
                Check if the last post date is more recent than the
                storyhost's last scraped date. If it's not, skip it.

                If it is, update the last scraped date, and add it to the
                list of url_stories to be returned at the end of this function.
            """

            last_seg_date = self.get_last_seg_date(story)
            if thread_url is not None:
                if last_post_date > storyhost.last_scraped or last_seg_date < last_post_date:
                    storyhost.last_scraped = cur_date
                    storyhost.save()
                    thread_link = response.urljoin(thread_url)

                    # Add this story to two separate lists, one for updating, one for just
                    # scraping.
                    if created:
                        url_stories.append((thread_link, story))
                    else:
                        self.update_list.append(("{0}threadmarks".format(thread_link), story))
                else:
                    print("Skipping {0}".format(storyhost.url))

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

        # div_tmarks is a list of all threadmarked posts on this story thread
        # ...at least on this PAGE of the story.
        div_tmarks = response.xpath("//li[contains(@class, 'hasThreadmark')]")
        
        if div_tmarks is not None and len(div_tmarks) > 0:

            for div_tmark in div_tmarks:
                # story_seg = StorySegment()

                author = div_tmark.xpath("@data-author").extract_first()

                author_seg, created = Author.objects.get_or_create(name=author)

                title = "".join(div_tmark.xpath("div/span/text()").extract()).encode('utf-8')
                title = " ".join(title.split())

                # Get the Date and clean it up/format it ======================================
                date = div_tmark.xpath(".//span[@class='DateTime' and ../@class!='editDate']/@title").extract_first()
                if date is None:
                    date = div_tmark.xpath(".//abbr[@class='DateTime']/text()").extract_first()
                date_obj = datetime.strptime(date, "%b %d, %Y at %I:%M %p")
                date_obj = date_obj.replace(tzinfo=utc)
                # story_seg.published = date_obj
                # =============================================================================

                story_seg, seg_created = StorySegment.objects.get_or_create(story=story_item,
                                                                            title=title,
                                                                            published=date_obj)

                # If you want to include the formatting of the original page, change the following
                # line to ..... .//blockquote/node()").extract()
                # As it stands, we don't necessarily need the <br /> tags and such.
                content = "".join(div_tmark.xpath(".//blockquote//text()").extract())
                story_seg.contents = content

                story_item.authors.add(author_seg)

                print("Title: {0}   Author: {1}".format(story_seg.title, author))
                print("date_time: {0}".format(date_obj))
                print("content length: {0}".format(len(content)))

                story_seg.save()
                story_item.save()

            div_next_tmark = div_tmarks[-1].xpath(".//span[@class='next']")

            # navigate to the next threadmark.
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

    def update_stories(self, response):
        """ This function will update a specific thread that already exists in the database.
        The response field already begins at the threadmarks page, and will scan the
        threadmark titles until it finds one that isn't in the story. Then it will simply
        send the scraping to the normal <scan_thread> method

        If all the threadmarks in the list are already created,
        it returns without sending any url requests to the website.

        :param response:
        :META param story_item:
        :return:
        """

        print("Scraping threadmarks at: {0}".format(response.url))
        story_item = response.meta.get("story_item")

        threadmarks_list = response.xpath("//li[contains(@class, 'threadmarkItem')]")

        url = None

        # scan the threadmarks until we reach one that **WAS NOT ALREADY CREATED***
        # get_or_create will return created to be TRUE, meaning this threadmark wasn't
        # already in the database. Set the url to that threadmark, and scan that thread.
        for tmark in threadmarks_list:
            chapter_title = "".join(tmark.xpath("./a/text()").extract()).encode('utf-8')
            chapter_title = " ".join(chapter_title.split())
            published_date = tmark.xpath(".//span[@class='DateTime']/@title").extract_first()
            if published_date is None:
                published_date = tmark.xpath(".//abbr[@class='DateTime']/text()").extract_first()
            published_date = datetime.strptime(published_date, "%b %d, %Y at %I:%M %p").replace(tzinfo=utc)

            print("Trying to update story: {0}".format(story_item.title))
            print("\tchapter title: {0}  date: {1}".format(chapter_title, published_date))

            story_seg, created = StorySegment.objects.get_or_create(story=story_item,
                                                                    title=chapter_title,
                                                                    published=published_date)
            if created:
                url = tmark.xpath("./a/@href").extract_first()
                url = response.urljoin(url)
                break

        if url is not None:
            # Set priority to slightly higher, and make sure to pass in the corresponding story_item.
            yield scrapy.Request(url=url, callback=self.scan_thread, priority=2, meta={"story_item": story_item})

    def get_last_seg_date(self, story):
        """ return the datetime object of the last segment in this story.

        will query the database for the last published story segment of <story>
        and return the datetime value for <published>

        If the <story> object doesn't have any segments associated with it, it returns
        the minimum date_time object.

        :param story:
        :return: datetime object
        """

        # retrieve the LAST story segment (ordered by published date)
        # if this entry doesn't exist, there are no story segments. Return the
        # oldest possible date.

        # ...various errors due to unicode problems....due to the data coming from either
        # the database, or the website. Not quite sure what is going on here, whether it's my
        # system, or not. But this code makes it work for the lowest common denominator.
        try:
            story_segs = StorySegment.objects.filter(story=story).order_by("-published")[0]
            """
            try:
                print ("lastdate for {0}: {1}".format(story.title, story_segs.published))
            except UnicodeEncodeError:
                print ("lastdate for {0}: {1}".format(story.title.encode('utf-8'), story_segs.published))
            """
            return story_segs.published
        except IndexError:
            """
            try:
                print(" no lastdate found for story [{0}]".format(story.title))
            except UnicodeEncodeError:
                print(" no lastdate found for story [{0}]".format(story.title.encode('utf-8')))
            """
            return datetime.min.replace(tzinfo=utc)

