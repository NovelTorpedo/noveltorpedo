import datetime
import fetch_tumblr

from noveltorpedo import models
from django.test import TestCase

class MockPost(object):
    def __init__(self, title=""):
        super(MockPost, self).__init__()
        self._title = title
        self._body = ""
        self._timestamp = (datetime.datetime.now() -
                          datetime.datetime.fromtimestamp(0)).total_seconds()

    def body(self, body=""):
        self._body = body
        return self

class MockBlog(object):
    def __init__(self, blog_name, blog_title, nsfw):
        super(MockBlog, self).__init__()
        self._name = blog_name
        self._title = blog_title
        self._nsfw = nsfw
        self._posts = []

    def add_post(self, post):
        self._posts.append(post)

class MockTumblrClient(object):
    def __init__(self):
        super(MockTumblrClient, self).__init__()
        self._blogs = {}

    def add_blog(self, blog):
        self._blogs[blog.name] = blog

    def blog_info(self, blog_name):
        """
        Needs to return a dictionary with the key "blog"
        which itself is a dictionary with keys "is_nsfw"
        (bool) and "title" (string).
        """
        # If this fails it will raise a KeyError, as the real pytumblr does.
        blog = self._blogs[blog_name]
        return {"blog":dict(blog)}

    def posts(self, blog_name, **kwargs):
        """
        Expects type=text, filter=text, offset integer,
        and limit an integer up to 20. Returns a dictionary
        with the key "posts" containing a list of
        dictionaries with keys "timestamp" "title" "body"
        """
        # If this fails it will raise a KeyError, as the real pytumblr does.
        blog = self._blogs[blog_name]
        return {"posts":map(dict, blog.posts)}

class TumblrTests(TestCase):
    def setUp(self):
        client = MockTumblrClient()
        blog = MockBlog("mock_blog", "My Mockup Blog", False)
        post = MockPost("Title of the Post").body("Contents of the post.")
        blog.add_post(post)
        fetch_tumblr.client = client

    def test_emptytest(self):
        print("Yay, a test.")
