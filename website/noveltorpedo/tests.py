from django.test import TestCase
from django.test import Client
from noveltorpedo.models import *

client = Client()


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')


class ModelTests(TestCase):

    def test_that_models_insert_and_retreieve(self):
        author_name = "test name"
        story_title = "The Big Lebowski"
        story_contents = "A long time ago in a galaxy far far away"

        author = Author()
        author.name = author_name
        author.save()

        story = Story()
        story.title = story_title
        story.contents = story_contents
        story.save()
        story.authors.add(author)

        # Grab the story.
        story = Story.objects.filter(title=story_title).first()
        self.assertEqual(story.title, story_title)
        self.assertEqual(story.contents, story_contents)

        # Grab the author from the story.
        author = story.authors.first()
        self.assertEqual(author.name, author_name)
