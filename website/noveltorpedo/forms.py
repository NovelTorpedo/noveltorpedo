# Copyright 2017 Brook Boese, Finn Ellis, Jacob Martin, Matthew Popescu, Rubin Stricklin, and Sage Callon
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import Form
from noveltorpedo.models import StoryHost
import requests
from subprocess import call
from os import walk, path

class SearchForm(HaystackSearchForm):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RegistrationForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class TumblrAddForm(Form):

    name = forms.CharField(required=True, label='Tumblr Username')

    def clean_name(self):
        name = self.cleaned_data.get("name")
        url = 'http://' + name + '.tumblr.com'

        if StoryHost.objects.filter(url=url).count():
            raise forms.ValidationError('We\'re already tracking stories from ' + name + ' on Tumblr.')

        if requests.get(url).status_code != 200:
            raise forms.ValidationError(name + ' is not a valid username on Tumblr')

        return name

    def save(self):
        name = self.clean_name()
        fetch_tumblr = self.get_scraper_location("fetch_tumblr.py")
        call(["python2", fetch_tumblr, name])

    def get_scraper_location(self, file_name):

        noveltorpedo_dir = path.abspath(__file__).rsplit("website")[0][:-1]

        for root, dirs, files in walk(noveltorpedo_dir):
            if file_name in files:
                return path.join(root, file_name)
