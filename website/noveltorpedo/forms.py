from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import BaseForm
from noveltorpedo.models import StoryHost
import requests


class SearchForm(HaystackSearchForm):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

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


class TumblrAddForm(BaseForm):

    name = forms.CharField(required=True)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        url = name + '.tumblr.com'

        if StoryHost.objects.filter(url=url).count():
            raise forms.ValidationError('We already be trackin dat')

        if requests.get(url).status_code != 200:
            raise forms.ValidationError('That aint no Tumblr')
