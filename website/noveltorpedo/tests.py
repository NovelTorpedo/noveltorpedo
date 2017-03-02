from django.test import TestCase
from django.test import Client
from noveltorpedo.models import *
from django.utils import timezone
from django.core.management import call_command

client = Client()


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')

    def test_insertion_and_querying_of_data(self):
        # Create a new story in the database.
        author = Author()
        author.name = 'Jack Frost'
        author.save()

        story = Story()
        story.title = 'The Big One'
        story.save()

        story.authors.add(author)

        segment = StorySegment()
        segment.published = timezone.now()
        segment.story = story
        segment.title = 'Chapter Three'
        segment.contents = 'This is how it all went down...'
        segment.save()

        # Index the new story.
        call_command('update_index')

        # Query via author name.
        response = client.get('/', {'q': 'Jack Frost'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jack Frost')
        self.assertContains(response, 'The Big One')
        self.assertContains(response, 'Chapter Three')
        self.assertContains(response, 'This is how it all went down...')

        # Query via story name.
        response = client.get('/', {'q': 'The Big One'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jack Frost')
        self.assertContains(response, 'The Big One')
        self.assertContains(response, 'Chapter Three')
        self.assertContains(response, 'This is how it all went down...')

        # Query via segment contents.
        response = client.get('/', {'q': 'Chapter Three'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jack Frost')
        self.assertContains(response, 'The Big One')
        self.assertContains(response, 'Chapter Three')
        self.assertContains(response, 'This is how it all went down...')
