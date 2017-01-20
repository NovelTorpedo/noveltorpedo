from django.conf.urls import include, url
from . import views

app_name = 'noveltorpedo'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^search/$', include('haystack.urls')),
]
