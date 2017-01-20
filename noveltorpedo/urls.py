from django.conf.urls import include, url
from . import views

app_name = 'noveltorpedo'

urlpatterns = [
    url(r'^$', include('haystack.urls')),
]
