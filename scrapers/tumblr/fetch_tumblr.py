#!/usr/bin/python

# For inserting well-formed TZ-aware post dates into the database.
from datetime import datetime, timedelta
from pytz import utc

# So we can pause between API calls, per Tumblr's robots.txt.
from time import sleep

# Library for API calls, and secondary file with authentication keys.
import pytumblr
from secrets import consumer_key, secret_key, oauth_token, oauth_secret

# All of this is just so we can get and use the Django models for DB objects.
import django
from django.conf import settings
from django.db import connection
import sys
import os

sys.path.insert(0, "../../website")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from noveltorpedo import models


class TumblrNotFound(ValueError):
    pass


# The host is a Host DB object which will be initialized later.
# TODO: Do this here, once, with get_or_create() instead.
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
        # Not using get_or_create() here, because if it doesn't exist, we
        # have more work to do than just creating a single object.
        storyhost = models.StoryHost.objects.get(url = blog + ".tumblr.com")
    except models.StoryHost.DoesNotExist:
        try:
            blog_info = client.blog_info(blog)["blog"]
        except KeyError:
            raise TumblrNotFound(blog)
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
        # We initialize the last scraped time to the earliest time a datetime
        # can store. This is easier to compare later than a null value.
        storyhost.last_scraped = datetime.min.replace(tzinfo=utc)
        storyhost.save()
    return storyhost

def update_continuously(idle_time=10, minimum_delay=10):
    """Loops indefinitely, updating the database with new posts to Tumblr blogs.

    Specifically, finds the Tumblr StoryHost which is least recently updated,
    and if that update is longer ago than the minimum delay, checks it for new
    posts.

    Args:
        idle_time: Time, in seconds, to sleep when there's nothing to do.
        minimum_delay: Minimum time, in seconds, to wait before requesting
            updates to the same blog again.
    """
    print("Entering continuous update loop.")
    while True:
        try:
            storyhost = models.StoryHost.objects.filter(host=get_host()).earliest("last_scraped")
        except models.StoryHost.DoesNotExist:
            print("No storyhosts found. Idling for {0} seconds.".format(idle_time))
            sleep(idle_time)
            continue
        if datetime.now(utc) - storyhost.last_scraped < timedelta(seconds=minimum_delay):
            print("Least recent storyhost update is less than {0} seconds "
                  "old. Idling for {1} seconds.".format(minimum_delay, idle_time))
            sleep(idle_time)
            continue
        print("Checking for updates to {0}.".format(storyhost.story))
        update_story(storyhost)

def update_story(storyhost):
    """
    Retrieve any posts which have been added to a story since its last
    scraped timestamp. Takes a StoryHost object where the host is Tumblr, and
    returns nothing.
    """
    # Start at the most recent post.
    offset = 0
    posts = get_posts(storyhost.url)
    try:
        post = posts.pop(0)
    except IndexError:
        # Blog has no text posts at all.
        # Set this in a way that will skip the update loop.
        post_date = storyhost.last_scraped
    else:
        post_date = datetime.fromtimestamp(post["timestamp"], utc)
    while post_date > storyhost.last_scraped:
        # Loop through posts, one at a time, as long as the current post we're
        # examining is more recent than the last time we updated the story.
        segment = models.StorySegment()
        segment.story = storyhost.story
        segment.title = post["title"]
        segment.contents = post["body"]
        segment.published = post_date
        segment.save()
        # TODO: Use an actual logger.
        print("Adding segment: " + segment)
        try:
            post = posts.pop(0)
        except IndexError:
            # No more posts remain from the last API call.
            # Wait the amount of time that robots.txt requests, then
            # make another call to get more posts.
            sleep(get_host().wait)
            offset = offset + MAX_POSTS
            posts = get_posts(storyhost.url, offset)
            try:
                post = posts.pop(0)
            except IndexError:
                # We got no posts from the new API call.
                # That means we've run out of posts overall.
                break
        # If we get back out here, we have a new post to loop on.
        post_date = datetime.fromtimestamp(post["timestamp"], utc)
    storyhost.last_scraped = datetime.now(utc)
    storyhost.save()

def get_posts(blog, offset=0, limit=MAX_POSTS):
    """
    Fetch post contents and metadata. Parameters:
        blog (the short name of the blog)
        offset (how many posts back to begin)
        limit (how many posts to return; 20 is the max allowed by the API)
    Returns a list of dictionaries of post information.
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    """
    Takes the username of a tumblr account on the command line and adds the
    corresponding story entry to the database, iff the account exists.

    If no username is supplied, instead enters a loop of updating the least
    recently updated Tumblr stories in the database.
    """
    try:
        create_story(sys.argv[1])
    except TumblrNotFound as e:
        print("No such tumblr: " + str(e))
    except IndexError:
        update_continuously()
