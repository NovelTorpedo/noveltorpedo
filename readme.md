## Installation Notes

Install dependencies:
```bash
sudo apt update
sudo apt install python3-django
sudo apt install python3-django-haystack
sudo apt install python3-yaml
sudo apt install python3-psycopg2 # PostgreSQL adapter for Python
```

Database setup, with fresh empty database:
```bash
python3 manage.py migrate
python3 manage.py loaddata search/fixtures/*.yaml
```
