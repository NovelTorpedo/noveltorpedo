from django import forms
from haystack.forms import SearchForm as HaystackSearchForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
