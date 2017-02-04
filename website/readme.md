## Installation Notes

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
configuration is fine).

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

## Database / Search Index Migrations and Seeding

Database setup, with fresh empty database:
```bash
python3 manage.py migrate
python3 manage.py seed
python3 manage.py rebuild_index
```

## Development Notes

To run the development server:
```bash
python3 manage.py runserver
```

To run all tests:
```bash
python3 manage.py test
```
