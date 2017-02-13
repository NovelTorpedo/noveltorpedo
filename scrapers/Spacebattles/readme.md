Navigate to the "noveltorpedo/scrapers/Spacebattles" directory
before proceeding.

It is recommended to run scrapy using a virtualenv
Oftentimes, scrapy dependencies conflict with common system libraries
Install python dependencies:
```
pip install -r requirements_linux.txt
```
(Windows)
```
pip install -r requirements_win.txt
```

Start up elasticsearch and database.
Instructions to set up back end and front end [here](../../website)

Run scraper:
```
scrapy crawl sb_spider
```


To see results, update the index of the database. (Instructions in the website readme)
