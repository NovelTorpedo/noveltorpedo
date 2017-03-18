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


from django.db import models


class Host(models.Model):
    """
    Each Host entity is a website/source that we scrape, e.g. spacebattles.com.
    """
    url = models.CharField(max_length=512)
    spider = models.CharField(max_length=255)
    wait = models.IntegerField()

    def __str__(self):
        return self.url


class Author(models.Model):
    """
    Each Author entity is associated with one or more Story entities.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AuthorAttribute(models.Model):
    """
    @TODO:  Enforce required attributes that each Author entity must have.
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=512)

    class Meta:
        db_table = 'noveltorpedo_author_attributes'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.key


class Story(models.Model):
    """
    Each Story entity is comprised of one or more Segment entities.
    """
    authors = models.ManyToManyField(Author)
    hosts = models.ManyToManyField(Host, through='StoryHost')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class StoryAttribute(models.Model):
    """
    @TODO:  Enforce required attributes that each Story entity must have.
    """
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=512)

    class Meta:
        db_table = 'noveltorpedo_story_attributes'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.key


class StoryHost(models.Model):
    """
    This model serves to store additional pivot fields for url and the date last scraped.
    """
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    url = models.CharField(max_length=1024)
    last_scraped = models.DateTimeField()

    class Meta:
        db_table = 'noveltorpedo_story_hosts'


class StorySegment(models.Model):
    """
    Each StorySegment entity comprises a body of text, for instance a single chapter of a story.
    """
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    title = models.CharField(max_length=512, null=True)
    contents = models.TextField(default='')
    published = models.DateTimeField()

    class Meta:
        db_table = 'noveltorpedo_story_segments'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.published.__str__()
