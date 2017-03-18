#!/usr/bin/python

# Copyright 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu, Rubin Stricklin, and Sage Callon
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Tumblr post fetcher for NovelTorpedo
https://github.com/NovelTorpedo/noveltorpedo

(c) 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu,
    Rubin Stricklin, and Sage Callon.

You are free to use, copy, modify, and distribute this file, with attribution,
under the terms of the MIT license. See LICENSE.txt for details.
"""

# For inserting well-formed TZ-aware post dates into the database.
from datetime import datetime, timedelta
from pytz import utc

# So we can pause between API calls, per Tumblr's robots.txt.
from time import sleep

# For proper log message handling.
import logging

# Library for API calls, and secondary file with authentication keys.
import pytumblr
try:
    from secrets import consumer_key, secret_key, oauth_token, oauth_secret
except ImportError:
    print("Couldn't import authorization secrets. This is normal if you're "
           "running tests. If you aren't running tests, you need to create a "
           "secrets.py with your Tumblr authentication details; see README.md "
           "for more information.")

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


# This is defined by Tumblr's API.
MAX_POSTS = 20

# Grab the Host object from the database and a client for connecting to the
# Tumblr API, since we'll need these in a couple of places.
host_attrs = {"url": "tumblr.com",
              "spider": "tumblr/fetch_tumblr.py",
              "wait": 1}
tumblr = models.Host.objects.get_or_create(**host_attrs)[0]
try:
    client = pytumblr.TumblrRestClient(consumer_key, secret_key,
                                       oauth_token, oauth_secret)
except NameError:
    print("Couldn't initialize client. This is normal if you're running tests.")

# Initialize the logger with basic stream output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

def get_or_create_storyhost(blog):
    """Finds the StoryHost for a Tumblr blog, creating it if necessary.

    Either fetches the StoryHost corresponding to the given Tumblr username
    or creates it, initializing appropriate author and story rows at the same
    time. Doesn't currently handle the case where the blog has been added and
    then deleted, so could conceivably return a database entry for a blog
    that no longer exists.

    Args:
        blog: The username of a Tumblr blog (e.g. "litrocket-test").

    Returns:
        A StoryHost object corresponding to the given blog.

    Raises:
        TumblrNotFound: If there is no such blog and no existing StoryHost.
    """
    try:
        # Not using get_or_create() here, because if it doesn't exist, we
        # have more work to do than just creating a single object.
        storyhost = models.StoryHost.objects.get(url=blog+".tumblr.com")
    except models.StoryHost.DoesNotExist:
        try:
            blog_info = client.blog_info(blog)["blog"]
        except KeyError:
            raise TumblrNotFound(blog)
        story = models.Story()
        story.title = blog_info["title"]
        story.save()

        if blog_info["is_nsfw"]:
            nsfw = models.StoryAttribute()
            nsfw.story = story
            nsfw.key = "nsfw"
            nsfw.value = "TRUE"
            nsfw.save()

        author = models.Author()
        author.name = blog
        author.save()
        story.authors.add(author)

        storyhost = models.StoryHost()
        storyhost.host = tumblr
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
    posts. Then repeats.

    Args:
        idle_time: Time, in seconds, to sleep when there's nothing to do.
        minimum_delay: Minimum time, in seconds, to wait before requesting
            updates to the same blog again.
    """
    logger.info("Entering continuous update loop.")
    while True:
        try:
            sh_manager = models.StoryHost.objects
            storyhost = sh_manager.filter(host=tumblr).earliest("last_scraped")
        except models.StoryHost.DoesNotExist:
            logger.debug("No storyhosts found. Idling for %s seconds.",
                         idle_time)
            sleep(idle_time)
            continue
        if (datetime.now(utc) - storyhost.last_scraped
                < timedelta(seconds=minimum_delay)):
            logger.debug("Least recent storyhost update is less than %s "
                         "seconds old. Idling for %s seconds.",
                         minimum_delay, idle_time)
            sleep(idle_time)
            continue
        logger.debug("Checking for updates to %s.", storyhost.story)
        update_story(storyhost)

def update_story(storyhost):
    """Fetches updates to the story corresponding to the given StoryHost.

    Makes one or more calls to the Tumblr API, adding segment entries for any
    posts which were published more recently than the last_updated value for
    the StoryHost. Will not currently notice posts that are backdated,
    deleted, or edited. Returns nothing.

    Args:
        storyhost: an existing StoryHost object.
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
        logger.debug("Adding segment: " + str(segment))
        try:
            post = posts.pop(0)
        except IndexError:
            # No more posts remain from the last API call.
            # Wait the amount of time that robots.txt requests, then
            # make another call to get more posts.
            sleep(tumblr.wait)
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
    """Retrieves some text posts by the given account from the Tumblr API.

    Makes one call to the Tumblr API, requesting posts with the given
    parameters. Only asks for text posts, in the format that the user entered
    them (which may include HTML or Markdown, but needn't).

    Args:
        blog: The username of a Tumblr blog (e.g. "litrocket-test").
        offset: How many posts back from the most recent one to begin.
        limit: How many total posts to retrieve (bounded by the maximum
            defined by the API).

    Returns:
        A list of dictionaries, each one corresponding to a post, in
        descending order by publication timestamp. Relevant keys include
        "timestamp" (publication time in seconds since the epoch in UTC),
        "title", and "body".
    """
    return client.posts(blog, type="text", filter="text",
                        offset=offset, limit=limit)["posts"]

if __name__ == "__main__":
    """Add a Tumblr blog to the database, or start the update loop.

    If a username is given, attempts to add appropriate entries to the
    database (story, storyhost, and author) for that Tumblr account. Will
    not add it if those entries already exist, or if there is no such blog,
    but also won't notice if those entries already exist but the blog does
    not any more.

    With no arguments, will just start an infinite loop of checking for
    updates to the stories already recorded in the database. (Adding new
    stories while it's going, by running another instance with an argument
    or calling the get_or_create_storyhost() function from elsewhere, works
    and is the intended use case.)

    Command Line Args:
        (optional) The username of a Tumblr account (e.g. "litrocket-test").
    """
    try:
        get_or_create_storyhost(sys.argv[1])
    except TumblrNotFound as e:
        logger.error("No such tumblr: " + str(e))
    except IndexError:
        update_continuously()
