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


"""
Description:
This scraper crawls on the creative writing archive page of spacebattles.com.
It was not known whether this source was updated on a regular basis, but recent
activity suggests it is updated several times a day.

The format of the archive threads disallow comments, so it is possible to just 
scrape every post.
"""


class StorySpider(scrapy.Spider):
    name = "storyarchive"

    def start_requests(self):
        urls = [
            "https://forums.spacebattles.com/forums/creative-writing-archive.40/"
        ]
        
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
                
        #insert while loop here later to scan THROUGH the threads

        # ------
        current_page = response.xpath("//a[@class='currentPage ']/text()")
        print("current page: {0}".format(current_page.extract_first()))

        next_page_link = response.xpath("//a[@class='text' and contains(., 'Next')]")
        next_page_link = next_page_link.xpath('@href').extract_first()

        if next_page_link is not None:

            #print("next page link: {0}".format(next_page_link))
            next_page_link = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_link, callback=self.parse)

        #self.parse_page(response)

    def parse_page(self, response):
        print("scraping {0}".format(response.url))

        li_tags = response.xpath("//li[@class='discussionListItem visible  ']")

        #thread_li_tags = self.get_start_node(li_tags) 
        
        for thread_tag in li_tags:
            author = thread_tag.xpath('@data-author').extract()
            print("authors: {0}".format(author))
