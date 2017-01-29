from django.contrib import admin

from noveltorpedo.models import *

admin.site.register(Host)
admin.site.register(Author)
admin.site.register(AuthorAttribute)
admin.site.register(Story)
admin.site.register(StoryAttribute)
admin.site.register(StorySegment)
