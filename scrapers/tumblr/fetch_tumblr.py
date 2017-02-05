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

host = None
client = pytumblr.TumblrRestClient(consumer_key, secret_key,
                                   oauth_token, oauth_secret)

# This is defined by Tumblr's API.
MAX_POSTS = 20

def get_host():
    """
    Retrieves the Tumblr host entry from the database, creating it first if it
    didn't already exist and caching it if it did. Returns a Host object.
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
    the corresponding StoryHost object. If it was already in the database,
    returns the existing one.
    """
    try:
        storyhost = models.StoryHost.objects.get(url = blog + ".tumblr.com")
    except models.StoryHost.DoesNotExist:
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
    return storyhost

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
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    """
    Takes the username of a tumblr account on the command line and adds its
    text posts to the database. Assumes the blog exists and has at least one
    text post.
    """
    try:
        blog = sys.argv[1]
    except IndexError:
        print("Please supply a tumblr name.")
    else:
        create_story(blog)
        update_story(blog)
