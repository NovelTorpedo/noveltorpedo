from django.test import TestCase
from django.test import Client
from noveltorpedo.models import *
import unittest
from django.utils import timezone

client = Client()


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')

    def test_insertion_and_querying_of_data(self):
        author = Author()
        author.name = "Jack Frost"
        author.save()

        story = Story()
        story.title = "The Big One"
        story.save()

        story.authors.add(author)

        segment = StorySegment()
        segment.published = timezone.now()
        segment.story = story
        segment.title = "Chapter One"
        segment.contents = "This is how it all went down..."
        segment.save()