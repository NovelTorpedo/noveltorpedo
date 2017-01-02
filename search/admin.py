from django.contrib import admin

from .models import Author, Story

admin.site.register(Author)
admin.site.register(Story)
