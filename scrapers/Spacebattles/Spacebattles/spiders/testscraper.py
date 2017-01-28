import scrapy


class StorySpider(scrapy.Spider):
    name = "stories_test"

    def start_requests(self):
        urls = [
            "https://forums.spacebattles.com/forums/creative-writing-archive.40"
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

        
        urls = self.get_thread_urls(response)
    
        for url in urls:
            yield scrapy.Request(url, callback=self.scan_thread)
        

        """
        if next_page_link is not None:

            #print("next page link: {0}".format(next_page_link))
            next_page_link = response.urljoin(next_page_link)
            yield scrapy.Request(next_page_link, callback=self.loop_pages)
        """

    def get_thread_urls(self, response):

        """ Scan the threads on a page

        Keyword arguments:
            response -- the response object used to navigate the page
        
        Return Value:
            ret      -- A list of urls to all threads on the page
        """

        print("scraping {0}".format(response.url))
        urls = []

        li_tags = response.xpath("//li[@class='discussionListItem visible  ']")

        for thread_tag in li_tags:
            author = thread_tag.xpath('@data-author').extract()
            a_node = thread_tag.xpath("div/div/h3/a")
            thread_url = a_node.xpath("@href").extract_first()

            #print("\nauthors: {0}".format(author))
            #print(  "    url: {0}".format(thread_url))

            if thread_url is not None:

                thread_link = response.urljoin(thread_url)
                urls.append(thread_link)
                #yield scrapy.Request(thread_link, callback=self.scan_thread)

        return urls

    def scan_thread(self, response):

        """ Scan the actual thread for story and author content

        Keyword arguments:
        response -- the response object used to navigate the page

        """

        print("\nscraping {0}\n".format(response.url))

        div_threadmarks = response.xpath("//div[@class='Menu threadmarksMenu']")

        if len(div_threadmarks) > 0:
            div_threadmark_url = div_threadmarks.xpath("div/a/@href").extract_first()
            threadmark_url = response.urljoin(div_threadmark_url)
            yield scrapy.Request(threadmark_url, callback=self.process_threadmarks)

    def process_threadmarks(self, response):
        
        """ extract all of the thread marks for this thread.

        Keyword Arguments:
            response -- the response object used to navigate the page

        Return Value:
            a list of threadmark urls for this thread

        """
        print("\nscraping {0}\n".format(response.url))
