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

from django.core.management import call_command
from django.test import TestCase
from django.test import Client
from django.utils import timezone
from noveltorpedo.models import *
from django.contrib.auth.models import User

client = Client()


class AuthTests(TestCase):

    def test_registration(self):
        # We can see the 'Login' button, but not the 'Logout' button since we haven't registered yet.
        response = client.get('/register')
        self.assertContains(response, 'Login')
        self.assertNotContains(response, 'Logout')
        self.assertContains(response, 'NovelTorpedo Registration')

        # Ensure validation is working.
        response = client.post('/register', {
            'username': 'johndoe',
            'email': 'john@test.com',
            'password1': 'thisisagoodpassword123',
            'password2': 'thisisapassword123',
        })
        self.assertContains(response, 'The two password fields didn&#39;t match.')

        # Ensure a successful registration redirects back to the home page with the user automatically logged in.
        response = client.post('/register', {
            'username': 'johndoe',
            'email': 'john@test.com',
            'password1': 'thisisagoodpassword123',
            'password2': 'thisisagoodpassword123',
        }, follow=True)
        self.assertRedirects(response, '/')

        # Now the user should be logged in, and so should see the 'Logout' button.
        response = client.get('/register')
        self.assertContains(response, 'Logout')
        self.assertNotContains(response, 'Login')

        # Sanity check that the user's information was properly saved.
        user = User.objects.last()
        self.assertEquals('johndoe', user.username)
        self.assertEquals('john@test.com', user.email)

    def test_login(self):
        # We can see the 'Login' button, but not the 'Logout' button since we haven't registered yet.
        response = client.get('/login/')
        self.assertContains(response, 'Login')
        self.assertNotContains(response, 'Logout')
        self.assertContains(response, 'NovelTorpedo Login')


class SearchTests(TestCase):

    def test_that_the_front_page_loads_properly(self):
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NovelTorpedo Search')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')

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

    def test_tumblr_add_form(self):
        # Check an invalid tumblr name.
        response = client.post('/submit', {
            'name': 'a'
        })
        self.assertContains(response, 'a is not a valid username on Tumblr')

        # Check a valid tumblr name.
        response = client.post('/submit', {
            'name': 'quotethat'
        })
        self.assertContains(response, 'Story submitted successfully.')
        self.assertEqual(StoryHost.objects.filter(url="quotethat.tumblr.com").count(), 1)
