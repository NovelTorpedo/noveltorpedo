@echo off
call scrapy crawl sb_spider -a generate_test=1 ^
                            -a test_url=%1 ^
                            -s HTTPCACHE_ENABLED=1 ^
                            -s HTTPCACHE_DIR=%2
