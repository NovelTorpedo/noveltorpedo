from django.test import TestCase
from django.test import Client
from noveltorpedo.models import *

client = Client()


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')

class DBTests(TestCase):

    def test_that_inserts_and_retreieves(self):
        test = Story
        test_author = Author
        test_author.name = "test name"
        test.authors = test_author
        test.title = "test title"
        test.contents = "test contents"

        test.save()

        all_entries = Story.objects.all()
        print(all_entries)
