"""
Tests for the Tumblr fetcher. Run with noveltorpedo/website/manage.py test
while in this directory.
"""

import datetime
import fetch_tumblr

from noveltorpedo import models
from django.test import TestCase

class MockBlog(object):
    def __init__(self, blog_name, blog_title, is_nsfw):
        super(MockBlog, self).__init__()
        self.name = blog_name
        self.title = blog_title
        self.is_nsfw = is_nsfw
        self.posts = []

    def add_post(self, title="", body=""):
        post = {}
        post["title"] = title
        post["body"] = body
        post["timestamp"] = (datetime.datetime.now() -
                          datetime.datetime.fromtimestamp(0)).total_seconds()
        self.posts.append(post)

class MockTumblrClient(object):
    def __init__(self):
        super(MockTumblrClient, self).__init__()
        self.blogs = {}

    def add_blog(self, blog):
        self.blogs[blog.name] = blog

    def blog_info(self, blog_name):
        """
        Needs to return a dictionary with the key "blog"
        which itself is a dictionary with keys "is_nsfw"
        (bool) and "title" (string).
        """
        # If this fails it will raise a KeyError, as the real pytumblr does.
        blog = self.blogs[blog_name]
        return {"blog":blog.__dict__}

    def posts(self, blog_name, **kwargs):
        """
        Expects type=text, filter=text, offset integer,
        and limit an integer up to 20. Returns a dictionary
        with the key "posts" containing a list of
        dictionaries with keys "timestamp" "title" "body"
        """
        # If this fails it will raise a KeyError, as the real pytumblr does.
        blog = self.blogs[blog_name]
        return {"posts":map(dict, blog.posts)}

class TumblrTests(TestCase):
    def setUp(self):
        fetch_tumblr.host_attrs["wait"] = 0
        fetch_tumblr.tumblr = models.Host.objects.get_or_create(**fetch_tumblr.host_attrs)[0]
        fetch_tumblr.client = MockTumblrClient()
        mock_blog = MockBlog("mock_blog", "My Mockup Blog", False)
        mock_blog.add_post("Title of the Post", "Contents of the post.")
        fetch_tumblr.client.add_blog(mock_blog)

    def test_create_storyhost(self):
        created_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        retrieved_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        self.assertEqual(created_sh, retrieved_sh)
