from django.test import TestCase
from django.test import Client

client = Client()


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')

class DBTests(TestCase):

    def test_that_inserts_and_retreieves(self):
        True