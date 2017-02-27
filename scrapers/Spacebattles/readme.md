Navigate to the "noveltorpedo/scrapers/Spacebattles" directory
before proceeding.

## Notes
It is recommended to run scrapy using a virtualenv
Oftentimes, scrapy dependencies conflict with common system libraries


## Linux Installation

Required packages
```
    sudo apt install libpq-dev python3-dev
```

Install python dependencies:
```
pip install -r requirements_linux.txt
```

## Windows Installation

Install [elasticsearch](https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-4) for Windows.

```
pip install -r requirements_win.txt
```

## Running the scrapers

Start up elasticsearch and database.
Instructions to set up back end and front end [here](../../website)

Run scraper:
```
scrapy crawl sb_spider
```


To see results, update the index of the database. Instructions found [here](../../website)



## Generating Test scenarios

In order to test the scraper, it needs to have access to cached http responses. You can generate a cached response
scenario with the following command:

```
scrapy crawl sb_spider -a generate_test=1 -s HTTPCACHE_ENABLED=1 -s HTTPCACHE_DIR=<directoryname>
```

This will scrape a single thread, and cache all responses in the specified directory name.
Default directory name is `httpcache`.
The cache directory can be found in `/noveltorpedo/scrapers/Spacebattles/.scrapy/<directoryname>`

## Testing the scraper

To quickly test the scraper, offline or online, run the appropriate `runtests` command
where <directoryname> is the test directory name mentioned in the previous section.

Windows:
```
runtests.bat <directoryname>
```

Linux:
```
./runtests_linux <directoryname>
```
