import scrapy
import time



class StorySpider(scrapy.Spider):
    name = "stories"
    

    thread_queue = []

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
        #insert while loop here later to scan THROUGH the threads

        # ------
        current_page = response.xpath("//a[@class='currentPage ']/text()")
        print("current page: {0}".format(current_page.extract_first()))

        next_page_link = response.xpath("//a[@class='text' and contains(., 'Next')]")
        next_page_link = next_page_link.xpath('@href').extract_first()

        urls = self.get_thread_urls(response)

        for url in urls:
            yield scrapy.Request(url, callback=self.scan_thread, priority=1) 
            
        
        
        
        #yield scrapy.Request(urls[0], callback=self.scan_thread)
        
        #TODO: ADD CHECK HERE to only proceed when the thread_queue is empty!!!
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

        This looks for any threadmarks, processes them, and
        follows the last threadmark's "next" link.
        If the page doesn't have any threadmarks, or there is
        no next link, it gracefully closes.


        Keyword arguments:
        response -- the response object used to navigate the page

        """

        print("\nscraping thread {0}\n".format(response.url))

        div_tmarks = response.xpath("//li[contains(@class, 'hasThreadmark')]")
        
        if div_tmarks is not None and len(div_tmarks) > 0:
            
            for div_tmark in div_tmarks:
                author = div_tmark.xpath("@data-author").extract()
                title = div_tmark.xpath("div/span/text()").extract()
            
                print("Title: {0}   Author: {1}".format(title, author))


            div_next_tmark = div_tmarks[-1].xpath(".//span[@class='next']")
            
            if div_next_tmark is not None:
                next_mark = div_next_tmark.xpath("a/@href").extract_first() 
                print("Next url: {0}".format(next_mark))
                next_mark_url = response.urljoin(next_mark)
                yield scrapy.Request(next_mark_url, callback=self.scan_thread, priority=2)




            



        




