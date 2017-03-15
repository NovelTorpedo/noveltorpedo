from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import Form
from noveltorpedo.models import StoryHost
import requests
from sys import path
from subprocess import call


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
        path.insert(0, "../scrapers/tumblr")
        call("python2 fetch_tumblr.py " + self.name)
