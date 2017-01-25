## Installation Notes

Install dependencies:
```bash
sudo apt update
sudo apt install python3-django             # 1.8.7-1ubuntu5.4
sudo apt install python3-elasticsearch      # 1.6.0-1
sudo apt install python3-yaml               # 3.11-3build1
sudo apt install python3-psycopg2           # 2.6.1-1build2

elasticsearch 2.4.4:  https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-4
django-haystack 2.6.0:  https://django-haystack.readthedocs.io/en/v2.6.0/index.html
postgresql 9.5+173
```

I am currently installing Haystack with pip, since the apt package `python3-django-haystack` is an older version:
```bash
sudo apt install python-pip
sudo pip install django-haystack 
```

## Database / Search Index Migrations and Seeding

Database setup, with fresh empty database:
```bash
python3 manage.py migrate
python3 manage.py loaddata noveltorpedo/fixtures/*.yaml
python3 manage.py rebuild_index
```
