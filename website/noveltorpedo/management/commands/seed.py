from django.core.management.base import BaseCommand
from django.db import connection
from noveltorpedo.models import *
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


def random_sentence():
    return (
        'The ' + random.choice(nouns) + ' ' + random.choice(verbs) + ' ' +
        random.choice(adverbs) + '.'
    )


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Create 20 random authors.
        authors = []
        for i in range(0, 20):
            author = Author()
            author.name = random_name()
            author.save()
            authors.append(author)

        # Create 20 random stories.
        for i in range(0, 20):
            story = Story()
            story.title = random_sentence()
            story.save()
            story.authors.add(random.choice(authors))
