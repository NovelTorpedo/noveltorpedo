from django.db import models


class Host(models.Model):
    baseurl = models.CharField(max_length=511)
    spider = models.CharField(max_length=255)
    wait = models.IntegerField()

    def __str__(self):
        return self.baseurl


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StoryHosts(models.Model):
    host_id = models.IntegerField()
    story_id = models.IntegerField()
    story_url = models.CharField(max_length=511)
    last_scraped = models.DateTimeField()

    class Meta:
        db_table = 'story_hosts'


class Story(models.Model):
    authors = models.ManyToManyField(Author)
    hosts = models.ManyToManyField(Host, through=StoryHosts)
    title = models.CharField(max_length=255)
    contents = models.TextField(default='')

    def __str__(self):
        return self.title


class StoryAttribute(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=511)

    class Meta:
        db_table = 'story_attributes'

    def __str__(self):
        return self.story.__str__() + ' - ' + self.key
