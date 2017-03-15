from django.conf.urls import include, url
from . import views

app_name = 'noveltorpedo'

urlpatterns = [
    url(r'^$', views.SearchView(), name='haystack_search'),
    url(r'^register', views.register, name='register'),
    url(r'^submit', views.submit_story_tumblr, name='submit_story_tumblr')
]
