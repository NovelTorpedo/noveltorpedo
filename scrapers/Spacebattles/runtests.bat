@echo off
call scrapy crawl sb_spider -s HTTPCACHE_ENABLED=1 -s HTTPCACHE_EXPIRATION_SECS=0 -s HTTPCACHE_STORAGE="scrapy.extensions.httpcache.FilesystemCacheStorage" -s HTTPCACHE_IGNORE_MISSING=1
