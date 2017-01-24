from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Story(models.Model):
    authors = models.ManyToManyField(Author)
    title = models.CharField(max_length=255)
    contents = models.TextField(default='')

    def __str__(self):
        return self.title


class StoryAttribute(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=511)
