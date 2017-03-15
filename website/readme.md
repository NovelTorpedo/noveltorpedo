## Table of Contents

* [Back-end Installation](#back-end-installation)
* [Front-end Installation](#front-end-installation)
* [Database / Search Index Schema Installation](#database--search-index-schema-installation)
* [Back-end Development Notes](#back-end-development-notes)
    * [Updating Models / Database Schema](#updating-models--database-schema)
* [Front-end Development Notes](#front-end-development-notes)
    * [JavaScript](#javascript)
    * [Sass / CSS](#sass--css)

***NOTE:***  Ensure you are in the `website` directory when executing the
website development commands throughout this documentation.

## Back-end Installation

Prerequisites:
 - Java 8
 - Node.js with working `node` command.

If `node --version` doesn't work, you may just need to:
```
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

Create a virtual environment and install all of the Python packages defined in `requirements.txt`.

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
sudo systemctl start elasticsearch
```

If you do not need to use the website's front-end, you may now skip to
[Database / Search Index Schema Installation](#database--search-index-schema-installation).

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

Install the front-end packages via yarn (this will resolve packages using the
`yarn.lock` file):
```bash
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

For the forgot password feature to work, you'll need to run an SMTP server. 
To run the debugging mail server provided:
```bash
python -m smtpd -n -c DebuggingServer localhost:1025
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

First, edit the models in `noveltorpedo/models.py`.

When you are satisfied, delete the existing migrations:
```bash
rm -f noveltorpedo/migrations/0001_initial.py
```

You can now re-generate the migrations:
```bash
python3 manage.py makemigrations
```

**Please commit and push the updated models/migrations to the `master` branch.**

Now that you have a new schema, you can "flush" your Postgres database like so:
```bash
DROP DATABASE noveltorpedo;
CREATE DATABASE noveltorpedo;
```

And then [install the new schema](#database--search-index-schema-installation).

## Front-end Development Notes

The file `gulpfile.js` defines all of our front-end build (gulp) configurations.

### JavaScript

All JavaScript should be written in [ECMAScript 6](http://es6-features.org/).

For cleanliness and ease-of-use, *all* JavaScript is loaded/defined in
`assets/js/main.js`.

That file looks like this:
```javascript
require('./bootstrap');

$(function() {
    // Global JavaScript can go here if you'd like.
});
```

Feel free to create other JavaScript files and load them through
`assets/js/bootstrap.js`.

For instance, if you create the file `assets/js/my-javascript-file.js`, you can
alter the bootstrap file to load your JavaScript like so (note the added line):

```javascript
window._ = require('lodash');
window.$ = window.jQuery = require('jquery');
require('bootstrap-sass');
require('./my-javascript-file'); // <-- Added this line.
```

### Sass / CSS

Similarly to JavaScript, *all* Sass/CSS is loaded through
`assets/sass/main.scss`.

Global CSS should be placed in `assets/sass/_global.scss`.

Feel free to create as many other scss files as you'd like, ensuring to prepend
them with an underscore and load them in `assets/sass/main.scss`.

For instance, if you create the file `assets/sass/_my-sass-file.scss`, you can
alter `assets/sass/main.scss` like so (note the added line):
```sass
@import "bootstrap";
@import "global";
@import "my-sass-file"; // <-- Added this line.
```
