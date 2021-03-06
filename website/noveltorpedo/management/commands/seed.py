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

from django.core.management.base import BaseCommand
from django.db import connection
from noveltorpedo.models import *
from datetime import datetime
import pytz
import random

# Seed data.
first_names = ['Noah', 'Emma', 'Liam', 'Olivia', 'Mason', 'Sophia']
last_names = ['Jones', 'Taylor', 'Williams', 'Brown']

nouns = ['dog', 'cat', 'human', 'robot']
verbs = ['killed', 'jumped', 'exploded', 'devoured']
adverbs = ['majestically', 'ruthlessly', 'relentlessly']


def random_name():
    return random.choice(first_names) + ' ' + random.choice(last_names)


def random_date():
    tz = pytz.timezone('US/Pacific-New')
    year = random.randint(1999, 2009)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return tz.localize(datetime(year, month, day, hour, minute, second))


def random_sentence():
    return (
        'The ' + random.choice(nouns) + ' ' + random.choice(verbs) + ' ' +
        random.choice(adverbs) + '.'
    )


def random_paragraph():
    paragraph = ''
    for _ in range(random.randint(5, 10)):
        paragraph += random_sentence() + ' '
    return paragraph


def random_chapter():
    chapter = ''
    for _ in range(random.randint(1, 10)):
        chapter += random_paragraph()
    return chapter


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Truncate the tables.
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE noveltorpedo_author CASCADE')
        cursor.execute('TRUNCATE TABLE noveltorpedo_story CASCADE')

        # Create 20 random authors.
        authors = []
        for _ in range(100):
            author = Author()
            author.name = random_name()
            author.save()
            authors.append(author)

        # Create 20 random stories.
        for _ in range(100):
            story = Story()
            story.title = random_sentence()
            story.save()

            # Add 1 to 3 random authors.
            for __ in range(random.randint(1, 3)):
                story.authors.add(random.choice(authors))

            # Add 1 to 5 random segments.
            for __ in range(random.randint(1, 5)):
                segment = StorySegment()
                segment.story = story
                segment.contents = random_chapter()
                segment.published = random_date()
                segment.save()
