This is the Tumblr fetcher for [NovelTorpedo](../..). It allows you to add
text posts from Tumblr blogs to your search index, and keep them updated when
new posts are added.


## Setup and Configuration

Follow the instructions to install at least the backend of the
[website](../../website) and set up the database. Then, install the Tumblr
API library:

```bash
pip install pytumblr
```

To authenticate with Tumblr and receive data from the API, you'll need an
account and a set of authentication keys. See
[Tumblr's API documentation](https://www.tumblr.com/docs/en/api/v2) for how to
get these. Once you have your keys, edit `example-secrets.py` and replace
"myconsumerkey" with your actual consumer key, and so on for the other values.
Then rename that file to `secrets.py`.


## Usage

From the command line, you have two options. If you run `fetch_tumblr.py`
without arguments, it will enter an update loop, where it checks for new
posts to Tumblr blogs it already knows about and adds them to the database.

```bash
./fetch_tumblr.py
```

To add a blog to the database, pass the short name (username) of that blog
as an argument. (You can do this while the continuous update loop is running.)

```bash
./fetch_tumblr.py litrocket-test
```

You can also do either of these things by importing `fetch_tumblr.py` as a
module and calling its functions directly; the relevant functions are
`update_continuously` and `get_or_create_storyhost`, respectively. See the
docstrings for those functions for more information.
