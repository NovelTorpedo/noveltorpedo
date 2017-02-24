import datetime
import fetch_tumblr

from noveltorpedo import models
from django.test import TestCase

class MockPost(object):
    def __init__(self, title=""):
        self.title = title
        self.body = ""
        self.timestamp = datetime.datetime.now().timestamp()

class MockBlog(object):
    def __init__(self, blog_name, blog_title, nsfw):
        super().__init__()
        self.name = blog_name
        self.title = blog_title
        self.nsfw = nsfw
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

class MockTumblrClient(object):
    def __init__(self):
        super().__init__()
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
        return {"blog":dict(blog)}

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
        client = MockTumblrClient()
        blog = MockBlog("mock_blog", "My Mockup Blog", False)
        post = MockPost("Title of the Post")
        post.body = "Contents of the post."
        blog.add_post(post)
        fetch_tumblr.client = client

    def test_emptytest(self):
        print("Yay, a test.")
