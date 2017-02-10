Navigate to the "noveltorpedo/scrapers/Spacebattles" directory
before proceeding.

Install python dependencies:
```
pip install -r requirements_linux.txt
```
(Windows)
```
pip install -r requirements.txt
```

Start up elasticsearch and database.
Instructions to set up back end and front end [here](../../website)

Run scraper:
```
scrapy crawl stories
```


To see results, update the index of the database. (Instructions in the website readme)
