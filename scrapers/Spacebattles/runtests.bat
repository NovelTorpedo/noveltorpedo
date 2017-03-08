@echo off
REM Copyright 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu, Rubin Stricklin, and Sage Callon
REM Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
REM documentation files (the "Software"), to deal in the Software without restriction, including without limitation
REM the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
REM to permit persons to whom the Software is furnished to do so, subject to the following conditions:
REM The above copyright notice and this permission notice shall be included in all copies or substantial portions of
REM the Software.

REM THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
REM TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
REM THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
REM CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
REM IN THE SOFTWARE.

call python reset_db.py
call scrapy crawl sb_spider -s HTTPCACHE_ENABLED=1 -s HTTPCACHE_EXPIRATION_SECS=0 ^
                            -s HTTPCACHE_STORAGE="scrapy.extensions.httpcache.FilesystemCacheStorage" ^
                            -s HTTPCACHE_IGNORE_MISSING=1 ^
                            -s HTTPCACHE_DIR=%1