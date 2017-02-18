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

    # try to get the host object for this Host. Create if not found.
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

        # asynchronously try and update any stories...
        # self.update_stories(response)
        # return

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

            # Get the last post date for a thread ========================================================
            last_post_date = thread_tag.xpath(".//dl[@class='lastPostInfo']//abbr/text()").extract_first()
            if last_post_date is not None:
                date_obj = datetime.strptime(last_post_date, "%b %d, %Y at %I:%M %p")
                last_post_date = date_obj.replace(tzinfo=utc)
            # ============================================================================================

            author, created = Author.objects.get_or_create(name=author_name)
            if created:
                author.save()

            title = thread_tag.xpath(".//h3[@class='title']/a/text()").extract_first().encode('utf-8')
            story, created = Story.objects.get_or_create(title=title)
            if created:
                story.save()
            story.authors.add(author)

            a_node = thread_tag.xpath("div/div/h3/a")
            thread_url = a_node.xpath("@href").extract_first()

            cur_date = datetime.now(tz=utc)
            oldest_date = datetime.min
            oldest_date = oldest_date.replace(tzinfo=utc)

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
                if last_post_date > storyhost.last_scraped:
                    storyhost.last_scraped = cur_date
                    storyhost.save()
                    thread_link = response.urljoin(thread_url)
                    url_stories.append((thread_link, story))
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

                # If you want to include the formatting of the original page, change the following
                # line to ..... .//blockquote/node()").extract()
                content = "".join(div_tmark.xpath(".//blockquote//text()").extract())
                story_seg.contents = content

                print("Title: {0}   Author: {1}".format(story_seg.title, author))
                print("date_time: {0}".format(date_obj))
                print("content length: {0}".format(len(content)))

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

    def update_stories(self, response):
        """ Attempt to update all stories indexed in the database

        Makes queryset of all story objects, gets the storyhosts and segments,
        checks if the last segment available is older than the 'last scraped'
        field in the storyhost.

        :param self:
        :param response:
        :return:
        """
        story_hosts = []
        indexed_stories = Story.objects.all()

        for story in indexed_stories:
            try:
                story_host = StoryHost.objects.get(story=story, host=self.HOST)
                story_hosts.append(story_host)
                print("Updating story: {0}".format(story.title.encode('utf-8')))

            except django.core.exceptions.ObjectDoesNotExist:
                print("Couldn't find story: {0}".format(story.title.encode('utf-8')))

    def get_last_seg_date(self, story):
        """ return the datetime object of the last segment in this story.

        will query the database for the last published story segment of <story>
        and return the datetime value for <published>

        :param story:
        :return: datetime object
        """

        # retrieve the LAST story segment (ordered by published date)
        try:
            story_segs = StorySegment.objects.filter(story=story).order_by("published").reverse()[0]
            print ("lastdate for {0}: {1}".format(story.title, story_segs.published))
            return story_segs.published
        except IndexError:
            print(" no lastdate found for story [{0}]".format(story.title))
            return None

