from django.db import models


class Host(models.Model):
    """
    Each Host entity is a website/source that we scrape, e.g. spacebattles.com.
    """
    url = models.CharField(max_length=511)
    spider = models.CharField(max_length=255)
    wait = models.IntegerField()

    def __str__(self):
        return self.baseurl


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
    value = models.CharField(max_length=511)

    class Meta:
        db_table = 'author_attributes'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.key


class Story(models.Model):
    """
    Each Story entity is comprised of one or more Segment entities.
    """
    authors = models.ManyToManyField(Author)
    hosts = models.ManyToManyField(Host, through=StoryHost)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class StoryAttribute(models.Model):
    """
    @TODO:  Enforce required attributes that each Story entity must have.
    """
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=511)

    class Meta:
        db_table = 'story_attributes'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.key


class StoryHost(models.Model):
    """
    This model serves to store additional pivot fields for url and the date last scraped.
    """
    host = models.IntegerField()
    story = models.IntegerField()
    url = models.CharField(max_length=511)
    last_scraped = models.DateTimeField()

    class Meta:
        db_table = 'story_hosts'


class StorySegment(models.Model):
    """
    Each StorySegment entity comprises a body of text, for instance a single chapter of a story.
    """
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    title = models.TextField(max_length=511)
    contents = models.TextField(default='')
    published = models.DateTimeField()

    class Meta:
        db_table = 'story_segments'
