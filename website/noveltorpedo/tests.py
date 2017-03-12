from django.contrib import auth
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
