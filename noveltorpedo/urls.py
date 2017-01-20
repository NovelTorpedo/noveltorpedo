from django.conf.urls import include,url
from . import views

app_name = 'search'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search/$', include('haystack.urls')),
]
