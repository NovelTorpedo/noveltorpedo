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
