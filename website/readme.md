## Table of Contents

* [Back-end Installation](#back-end-installation)
* [Front-end Installation](#front-end-installation)
* [Database / Search Index Schema Installation](#database--search-index-schema-installation)
* [Back-end Development Notes](#back-end-development-notes)
    * [Updating Models / Database Schema](#updating-models-database-schema)

## Back-end Installation

Install Python dependencies:
```bash
sudo apt update
sudo apt install python3-django             # 1.8.7-1ubuntu5.4
sudo apt install python3-elasticsearch      # 1.6.0-1
sudo apt install python3-yaml               # 3.11-3build1
sudo apt install python3-psycopg2           # 2.6.1-1build2
sudo apt install python3-pip
sudo pip3 install django-haystack           # Latest (since apt `python3-django-haystack` is out-of-date)
```

Install PostgreSQL and create database:
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'secret';
CREATE DATABASE noveltorpedo;
```

Install [Elasticsearch 2.4.4](https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-4) (the default
configuration is fine):
```bash
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.4/elasticsearch-2.4.4.deb
sudo dpkg -i elasticsearch-2.4.4.deb
rm -f elasticsearch-2.4.4.deb
sudo systemctl enable elasticsearch.service
```

## Front-end Installation

Install [yarn](https://yarnpkg.com/):
```bash
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn
```

Install [gulp](http://gulpjs.com/) globally:
```bash
sudo yarn global add gulp
```

Install the front-end packages via yarn (this will resolve packages using the yarn.lock file):
```bash
cd website
yarn
```

To compile front-end assets (CSS/JS) once:
```bash
yarn run dev
```

To compile front-end assets (CSS/JS) continuously in real-time:
```bash
yarn run watch
```

## Database / Search Index Schema Installation

Database setup, with fresh empty database:
```bash
python3 manage.py migrate          # Create the Postgres tables.
python3 manage.py seed             # Populate the Postgres tables.
python3 manage.py rebuild_index    # Populate the Elasticsearch index.
```

## Back-end Development Notes

To run the development server:
```bash
python3 manage.py runserver
```

You can then visit the website at:
```bash
http://127.0.0.1:8000/
```

To run all tests:
```bash
python3 manage.py test
```

### Updating Models / Database Schema

First, edit the models in `website/noveltorpedo/models.py`.

When you are satisfied, delete the existing migrations:
```bash
rm -f noveltorpedo/migrations/0001_initial.py
```

And finally, re-generate the migrations:
```bash
python3 manage.py makemigrations
```

Now that you have a new schema, you can "flush" your Postgres database like so:
```bash
DROP DATABASE noveltorpedo;
CREATE DATABASE noveltorpedo;
```

And then [install the new schema](#database--search-index-schema-installation).
