#!/usr/bin/python

from datetime import datetime, MINYEAR
import pytumblr
from secrets import consumer_key, secret_key, oauth_token, oauth_secret

import django
from django.conf import settings
from django.db import connection
import sys
import os

sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from noveltorpedo import models

# These globals will be initialized later.
client = None   # Tumblr API client
host = None     # Tumblr Host object in the database

def get_info(blog):
    """
    Fetch general information about the blog being tracked. Returns a
    dictionary.  Keys which are likely to be useful:
        title
        url
        description
        is_nsfw (boolean)
        updated (most recent post's timestamp, in integer seconds since epoch)
    """
    return client.blog_info(blog)["blog"]

def get_posts(blog, offset=0, limit=20):
    """
    Fetch post contents and metadata. Parameters:
        offset (how many posts back to begin)
        limit (how many posts to return; 20 is the max allowed by the API)
    Returns a list of dictionaries. Keys which are likely to be useful:
        blog_name
        body
        post_url
        short_url
        timestamp
        title
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

def get_host():
    """
    Create the Tumblr host entry in the database iff it doesn't exist.
    In either case, returns the appropriate Host object, as well as saving
    it in a global variable so we don't have to query for it again.
    """
    global host
    if not host:
        host = models.Host.objects.filter(url = "tumblr.com").first()
    if not host:
        host = models.Host()
        host.url = "tumblr.com"
        host.spider = "scrapers/tumblr/fetch_tumblr.py"
        host.wait = 1 # per their robots.txt
        host.save()
    return host

def make_story(blog):
    """
    Add a new story to the database. Takes a Tumblr blog name and returns
    the corresponding Story object. Does no verification that the story
    hasn't already been added, and returns nothing.
    """
    blog_info = client.blog_info(blog)["blog"]
    story = models.Story()
    story.title = blog_info["title"]
    story.save()

    author = models.Author()
    author.name = blog
    author.save()
    story.authors.add(author)

    storyhost = models.StoryHost()
    storyhost.host = get_host()
    storyhost.url = blog + ".tumblr.com"
    storyhost.story = story
    storyhost.last_scraped = datetime(MINYEAR, 1, 1)
    storyhost.save()

if __name__ == "__main__":
    """
    This allows you to pass the short name of a tumblr on the command line to
    add it as a new entry to the story database. Doesn't retrieve posts yet.
    """
    import sys
    client = pytumblr.TumblrRestClient(consumer_key, secret_key, oauth_token,
                                       oauth_secret)
    try:
        blog = sys.argv[1]
        info = get_info(blog)
        posts = get_posts(blog)
    except IndexError:
        print("Please supply a tumblr name.")
        sys.exit(1)
    except KeyError:
        print("Tumblr not found.")
        sys.exit(1)

    make_story(blog)
