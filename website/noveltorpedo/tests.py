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
        segment.story = story
        segment.title = 'Chapter Three'
        segment.contents = 'Righteous justice was distributed...'
        segment.published = timezone.now()
        segment.save()

        # Index the new story.
        call_command('update_index')

        def check_response(response, highlighted_words=[]):
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Jack Frost')
            self.assertContains(response, 'The Big One')

            for word in highlighted_words:
                self.assertContains(response, '<span class="highlighted">' + word + '</span>')

        # Query via author name.
        check_response(client.get('/', {'q': 'Jack Frost'}))

        # Query via story title.
        check_response(client.get('/', {'q': 'The Big One'}))

        # Query via segment title.
        check_response(client.get('/', {'q': 'Chapter Three'}), ['Chapter', 'Three'])

        # Query via segment contents.
        check_response(client.get('/', {'q': 'Righteous justice'}, ['Righteous', 'justice']))
