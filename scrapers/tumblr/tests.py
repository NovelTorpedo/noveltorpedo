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
        return {"blog": self.blogs[blog_name].__dict__}

    def posts(self, blog_name, **kwargs):
        """
        Fetch the content of posts in the specified blog. This method assumes
        it's being called by fetch_tumblr.get_posts and has all the keyword
        arguments that function uses.

        Args:
            blog_name: The short_name or url of a MockBlog.
            offset: int, how many posts back (from most recent) to start.
            limit: int, how many posts to return.
            type: Ignored, should always be "text".
            filter: Ignored, should always be "text".

        Returns:
            A dictionary with one key, "posts", whose value is a list of
            dictionaries which each include the keys "title" and "body"
            (strings) and "timestamp" (a UNIX timestamp).

        Raises:
            KeyError: The requested MockBlog hasn't been added to the client.
        """
        # These are incidentally type assertions.
        assert(kwargs["type"] == "text")
        assert(kwargs["filter"] == "text")
        assert(kwargs["offset"] >= 0)
        assert(0 <= kwargs["limit"] <= fetch_tumblr.MAX_POSTS)
        # fetch_tumblr will pass blog urls, chop off the ".tumblr.com" part.
        blog_name = blog_name.split(".", 1)[0]
        all_posts = self.blogs[blog_name].posts
        # In production code I'd store them sorted instead, but in tests the
        # insert:retrieve ratio is so much higher that I think this is faster.
        all_posts.sort(key=lambda p: p["timestamp"], reverse=True)
        start = kwargs["offset"]
        end = kwargs["offset"] + kwargs["limit"]
        return {"posts": all_posts[start:end]}


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
        attrs = fetch_tumblr.host_attrs
        fetch_tumblr.tumblr = models.Host.objects.get_or_create(**attrs)[0]
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
        for i in xrange(1, count+1):
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

    def make_segments(self, blog_name):
        """
        Retrieve all story segments corresponding to a blog name from the
        database. Requires both that the blog has been added to the client
        with MockTumblrClient.add_blog(), and calls fetch_tumblr.update_story()
        to create the segments (if the blog has any posts in it).

        Args:
            blog_name: The short name of a MockBlog.

        Returns:
            A django QuerySet of StorySegment objects.
        """
        sh = fetch_tumblr.get_or_create_storyhost(blog_name)
        fetch_tumblr.update_story(sh)
        return models.StorySegment.objects.filter(story=sh.story)

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
            # Last scraped should be the oldest possible, because we haven't.
            self.assertEqual(sh.last_scraped,
                             datetime.min.replace(tzinfo=utc))
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
                    self.assertIsInstance(e,
                                          models.StoryAttribute.DoesNotExist)

    def test_get_posts(self):
        """
        Verify post retrieval from the client. This is honestly a test of the
        mock itself more than the fetcher, which is just a passthrough, but it
        does assert (in MockTumblrClient.posts()) that the right arguments are
        passed through.
        """
        self.add_long_blog(50)
        posts = fetch_tumblr.get_posts("long_blog")
        # No limit was specified, so we should've gotten the max.
        self.assertEqual(len(posts), fetch_tumblr.MAX_POSTS)
        # This is set in add_long_blog; what we're actually doing here
        # is verifying that the default offset was correct (0).
        self.assertEqual(posts[0]["timestamp"], 50)
        posts = fetch_tumblr.get_posts("long_blog", offset=1)
        self.assertEqual(posts[0]["timestamp"], 49)
        self.assertEqual(len(posts), 20)
        posts = fetch_tumblr.get_posts("long_blog", offset=100)
        self.assertEqual(len(posts), 0)
        posts = fetch_tumblr.get_posts("long_blog", offset=49)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["timestamp"], 1)
        posts = fetch_tumblr.get_posts("long_blog", limit=1)
        self.assertEqual(len(posts), 1)

    def test_update_finds_all(self):
        """
        Verify that update_story() will get all the posts, even if that takes
        many queries and doesn't end on an even multiple of the limit.
        """
        # A nice big prime number of posts.
        self.add_long_blog(111)
        segments = self.make_segments("long_blog")
        self.assertEqual(segments.count(), 111)
        oldest = segments.earliest("published")
        newest = segments.latest("published")
        self.assertEqual(oldest.title, "Post #1")
        self.assertEqual(newest.title, "Post #111")

    def test_update_gets_new(self):
        """
        Verify that update_story() adds new posts and only new posts.
        """
        self.add_simple_blog()
        segments = self.make_segments("mock_blog")
        self.assertEqual(segments.count(), 1)
        # Calling update again doesn't add any posts.
        segments = self.make_segments("mock_blog")
        self.assertEqual(segments.count(), 1)
        # Add another (empty) post, now there should be two.
        fetch_tumblr.client.blogs["mock_blog"].add_post()
        segments = self.make_segments("mock_blog")
        self.assertEqual(segments.count(), 2)

    def test_no_posts_no_problem(self):
        """
        Verify that update_story() handles empty blogs.
        """
        self.add_empty_blog()
        segments = self.make_segments("empty_blog")
        self.assertEqual(segments.count(), 0)
        # Really the assertion for this test is that no other error was raised.

    def test_segment_contents(self):
        """
        Verify that the inserted segment matches the post data.
        """
        self.add_empty_blog()
        post = {
            "title": "For a Good",
            "body": "Timestamp, call:",
            "timestamp": 8675309
            # (April 11, 1970, if you were wondering)
        }
        fetch_tumblr.client.blogs["empty_blog"].add_post(**post)
        segment = self.make_segments("empty_blog").first()
        self.assertEqual(segment.title, post["title"])
        self.assertEqual(segment.contents, post["body"])
        dt = datetime.fromtimestamp(post["timestamp"]).replace(tzinfo=utc)
        self.assertEqual(segment.published, dt)

    def test_last_scraped(self):
        """
        Verify that updating a story changes its last_scraped, whether or not
        new posts were found.
        """
        self.add_simple_blog()
        sh = fetch_tumblr.get_or_create_storyhost("mock_blog")
        old_scrape_date = sh.last_scraped
        fetch_tumblr.update_story(sh)
        self.assertNotEqual(old_scrape_date, sh.last_scraped)
        old_scrape_date = sh.last_scraped
        fetch_tumblr.client.blogs["mock_blog"].add_post()
        fetch_tumblr.update_story(sh)
        self.assertNotEqual(old_scrape_date, sh.last_scraped)
