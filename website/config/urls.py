"""
NovelTorpedo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views


urlpatterns = [
    url(r'^', include('noveltorpedo.urls')),
    url(r'^login/$', views.login, name='login', kwargs={'template_name': 'noveltorpedo/auth/login.html'}),
    url(r'^password_reset/$', views.password_reset, name='password_reset',
        kwargs={'template_name': 'noveltorpedo/auth/password_reset.html'}),
    url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done',
        kwargs={'template_name': 'noveltorpedo/auth/password_reset_done.html'}),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
]
