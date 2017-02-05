#!/usr/bin/python

from datetime import datetime
from pytz import utc
from time import sleep

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

# This is defined by Tumblr's API.
MAX_POSTS = 20

def get_host():
    """
    Create the Tumblr host entry in the database iff it doesn't exist.
    In either case, returns the appropriate Host object, as well as saving
    it in a global variable so we don't have to query for it again.
    """
    global host
    if not host:
        try:
            host = models.Host.objects.get(url = "tumblr.com")
        except models.Host.DoesNotExist:
            host = models.Host()
            host.url = "tumblr.com"
            host.spider = "scrapers/tumblr/fetch_tumblr.py"
            host.wait = 1 # per their robots.txt
            host.save()
    return host

def create_story(blog):
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
    storyhost.last_scraped = datetime.min.replace(tzinfo=utc)
    storyhost.save()

    print story
    print "---"

def update_story(blog):
    """
    Retrieve any posts which have been added to a story since its last
    scraped timestamp. Assumes that the story is already in the database,
    and there are text posts on the blog. Returns nothing.
    """
    storyhost = models.StoryHost.objects.get(url = blog + ".tumblr.com")
    oldest_new = datetime.now(utc)
    offset = 0
    posts = get_posts(blog)
    post = posts.pop(0)
    post_date = datetime.fromtimestamp(post["timestamp"], utc)
    while post_date > storyhost.last_scraped:
        segment = models.StorySegment()
        segment.story = storyhost.story
        segment.title = post["title"]
        segment.contents = post["body"]
        segment.published = oldest_new
        segment.save()
        print segment
        try:
            post = posts.pop(0)
        except IndexError:
            sleep(get_host().wait)
            offset = offset + MAX_POSTS
            posts = get_posts(blog, offset)
            if not posts:
                break
            post = posts.pop(0)
        post_date = datetime.fromtimestamp(post["timestamp"], utc)
    storyhost.last_scraped = datetime.now(utc)
    storyhost.save()

def get_posts(blog, offset=0, limit=MAX_POSTS):
    """
    Fetch post contents and metadata. Parameters:
        offset (how many posts back to begin)
        limit (how many posts to return; 20 is the max allowed by the API)
    Returns a list of dictionaries.
    TODO: Move the wait timer over here.
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    """
    This allows you to pass the short name of a tumblr on the command line to
    add it to the database, including its text posts.
    """
    import sys
    client = pytumblr.TumblrRestClient(consumer_key, secret_key, oauth_token,
                                       oauth_secret)
    try:
        blog = sys.argv[1]
        posts = get_posts(blog)
    except IndexError:
        print("Please supply a tumblr name.")
        sys.exit(1)
    except KeyError:
        print("Tumblr not found.")
        sys.exit(1)

    create_story(blog)
    update_story(blog)
