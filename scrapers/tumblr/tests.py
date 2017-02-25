"""
Tests for the Tumblr fetcher. Run with noveltorpedo/website/manage.py test
while in this directory.
"""

import fetch_tumblr

from datetime import datetime
from pytz import utc
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from noveltorpedo import models


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
            post["timestamp"] = (datetime.now() -
                                 datetime.fromtimestamp(0)).total_seconds()
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

    def add_simple_blog(self):
        """
        Insert a fake blog with one post.
        """
        mock_blog = MockBlog("mock_blog", "My Mockup Blog", False)
        mock_blog.add_post("Title of the Post", "Contents of the post.")
        fetch_tumblr.client.add_blog(mock_blog)

    def add_long_blog(self, count=111):
        """
        Insert a fake blog with many posts that have sequential timestamps.
        """
        long_blog = MockBlog("long_blog", "A Really Long Blog", False)
        for i in xrange(count):
            long_blog.add_post("Post #{0}".format(i), "", i)
        fetch_tumblr.client.add_blog(long_blog)

    def add_empty_blog(self):
        """
        Insert a fake blog with no posts.
        """
        empty_blog = MockBlog("empty_blog", "Shhhh.", False)
        fetch_tumblr.client.add_blog(empty_blog)

    def add_nsfw_blog(self):
        """
        Insert a fake blog that's marked NSFW.
        """
        nsfw_blog = MockBlog("nsfw_blog", "Don't Read This at Work!", True)
        nsfw_blog.add_post("A Raunchy Post", "This is not work-appropriate.")
        fetch_tumblr.client.add_blog(nsfw_blog)

    def test_get_create_storyhost(self):
        """
        Verify that get_or_create_storyhost does both of those things and
        returns the same StoryHost object for the same input.
        """
        self.add_simple_blog()
        created_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        retrieved_sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        self.assertIsInstance(created_sh, models.StoryHost)
        self.assertEqual(created_sh, retrieved_sh)

    def test_no_such_storyhost(self):
        """
        Verify that the appropriate exception is raised when the requested
        blog doesn't exist.
        """
        # No blogs exist at all.
        self.assertRaises(fetch_tumblr.TumblrNotFound,
                          fetch_tumblr.get_or_create_storyhost,
                          "nonexistent_blog")
        self.add_simple_blog()
        # A blog exists, but not the one we're looking for.
        self.assertRaises(fetch_tumblr.TumblrNotFound,
                          fetch_tumblr.get_or_create_storyhost,
                          "nonexistent_blog")
        self.add_simple_blog()

    def test_correct_storyhost(self):
        """
        Verify that get_or_create_storyhost inserts accurate blog info.
        """
        # Add some blogs to our imaginary Tumblr.
        self.add_simple_blog()
        self.add_nsfw_blog()
        blogs = fetch_tumblr.client.blogs
        for blog_name in ("mock_blog", "nsfw_blog"):
            # Create a storyhost in the database.
            fetch_tumblr.get_or_create_storyhost(blog_name)
            # Retrieve the storyhost from the database.
            sh = models.StoryHost.objects.get(url=blog_name+".tumblr.com")
            story = sh.story
            author = models.Author.objects.get(name=blog_name)
            # Check the storyhost's attributes.
            self.assertEqual(sh.host, fetch_tumblr.tumblr)
            # Last scraped should be the oldest possible, because we haven't yet.
            self.assertEqual(sh.last_scraped, datetime.min.replace(tzinfo=utc))
            # Check the story attributes.
            self.assertEqual(story.title, blogs[blog_name].title)
            # Tumblrs have exactly one author.
            self.assertEqual(story.authors.count(), 1)
            self.assertIn(author, story.authors.all())
            if blog_name is "nsfw_blog":
                # The following verifies there's exactly one attribute.
                attr = models.StoryAttribute.objects.get(story=story)
                self.assertEqual(attr.key, "nsfw")
                self.assertEqual(attr.value, "TRUE")
            else:
                # Doing this instead of assertRaises because of import path
                # weirdness, c.f. http://stackoverflow.com/q/549677/7619818
                # (If you can figure out how to make the plain assertRaises
                # work, by all means change this!)
                try:
                    attr = models.StoryAttribute.objects.get(story=story)
                except ObjectDoesNotExist as e:
                    # This is the superclass for all DoesNotExist errors.
                    self.assertIsInstance(e, models.StoryAttribute.DoesNotExist)

"""
Test brainstorm:
    * update finds new posts
    * update doesn't duplicate old posts
    * update finds all posts when post count > limit
    * update does nothing when there are no posts
    * update changes last_scraped in all the above cases
    * trivial test for get_posts? (just a passthrough to the mock really)
    * only text posts are requested
"""
