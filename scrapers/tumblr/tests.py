"""
Tests for the Tumblr fetcher. Run with noveltorpedo/website/manage.py test
while in this directory.
"""

import datetime
import fetch_tumblr

from noveltorpedo import models
from django.test import TestCase


class MockBlog(object):
    """
    A fake Tumblr blog to be retrieved by the mock client.
    """
    def __init__(self, blog_name, blog_title, is_nsfw):
        """
        Create a new mock blog.

        Args:
            blog_name: The short name of the blog (string, no spaces).
            blog_title: The blog title (string, spaces OK).
            is_nsfw: Boolean.
        """
        super(MockBlog, self).__init__()
        self.name = blog_name
        self.title = blog_title
        self.is_nsfw = is_nsfw
        self.posts = []

    def add_post(self, title="", body="", timestamp=None):
        """
        Add a post to the mock blog.

        Args:
            title: A string, defaults to empty.
            body: A string, defaults to empty.
            timestamp: UNIX timestamp, defaults to now.
        """
        post = {}
        post["title"] = title
        post["body"] = body
        if timestamp is None:
            post["timestamp"] = (datetime.datetime.now() -
                          datetime.datetime.fromtimestamp(0)).total_seconds()
        else:
            post["timestamp"] = timestamp
        self.posts.append(post)


class MockTumblrClient(object):
    """
    A mockup of the Tumblr API client provided by pytumblr, providing
    only the subset of its functionality used by fetch_tumblr.
    """
    def __init__(self):
        """
        Create a mock client and initialize the blog dict.
        """
        super(MockTumblrClient, self).__init__()
        self.blogs = {}

    def add_blog(self, blog):
        """
        Add a new mock blog so that it can be retrieved later.

        Args:
            blog: A MockBlog instance which may have posts in it.
        """
        self.blogs[blog.name] = blog

    def blog_info(self, blog_name):
        """
        Fetch general information about the specified blog. This mimics
        the pytumblr client's blog_info call. To make blogs available for
        finding, add them first with add_blog.

        Args:
            blog_name: The short name of a MockBlog.

        Returns:
            A dictionary with one key, "blog", whose value is another
            dictionary with keys including "title" and "body" (strings)
            and "is_nsfw" (boolean).

        Raises:
            KeyError: The requested MockBlog hasn't been added to the client.
        """
        return {"blog":self.blogs[blog_name].__dict__}

    def posts(self, blog_name, **kwargs):
        """
        Fetch the content of posts in the specified blog.
        TODO: Respect "offset" (int) and "limit" (int <= 20) arguments, and
        verify that "type" and "filter" arguments are both "text".

        Args:
            blog_name: The short name of a MockBlog.
            offset: int, how many posts back (from most recent) to start.
            limit: int, how many posts to return (20 max).
            type: Ignored, should always be "text".
            filter: Ignored, should always be "text".

        Returns:
            A dictionary with one key, "posts", whose value is a list of
            dictionaries which each include the keys "title" and "body" (strings)
            and "timestamp" (a UNIX timestamp).

        Raises:
            KeyError: The requested MockBlog hasn't been added to the client.
        """
        return {"posts":self.blogs[blog_name].posts}


class TumblrTests(TestCase):
    """
    Tests for fetch_tumblr.py.
    """
    def setUp(self):
        """
        Preparation to do before every test.
        """
        # We don't need to sleep between calls when just running tests.
        fetch_tumblr.host_attrs["wait"] = 0
        # Create the host entry for Tumblr in the database.
        fetch_tumblr.tumblr = models.Host.objects.get_or_create(**fetch_tumblr.host_attrs)[0]
        # Replace the pytumblr client with a mockup.
        fetch_tumblr.client = MockTumblrClient()
        # Insert a fake blog with one post.
        mock_blog = MockBlog("mock_blog", "My Mockup Blog", False)
        mock_blog.add_post("Title of the Post", "Contents of the post.")
        fetch_tumblr.client.add_blog(mock_blog)

    def test_create_storyhost(self):
        """
        Verify that get_or_create_storyhost does both of those things and
        returns the same StoryHost object for the same input.
        """
        created_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        retrieved_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        self.assertIsInstance(created_sh, models.StoryHost)
        self.assertEqual(created_sh, retrieved_sh)
