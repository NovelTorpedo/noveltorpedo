from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)


class Story(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    contents = models.TextField
