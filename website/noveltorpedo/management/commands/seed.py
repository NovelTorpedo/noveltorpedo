from django.core.management.base import BaseCommand
from django.db import connection
from noveltorpedo.models import *
from datetime import datetime
import pytz
import random

# Truncate the tables.
cursor = connection.cursor()
cursor.execute('TRUNCATE TABLE noveltorpedo_author CASCADE')
cursor.execute('TRUNCATE TABLE noveltorpedo_story CASCADE')

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
        # Create 20 random authors.
        authors = []
        for _ in range(20):
            author = Author()
            author.name = random_name()
            author.save()
            authors.append(author)

        # Create 20 random stories.
        for _ in range(20):
            story = Story()
            story.title = random_sentence()
            story.save()
            story.authors.add(random.choice(authors))

            for __ in range(random.randint(1, 5)):
                segment = StorySegment()
                segment.story = story
                segment.contents = random_chapter()
                segment.published = random_date()
                segment.save()
