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
