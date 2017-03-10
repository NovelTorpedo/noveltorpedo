from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from noveltorpedo.forms import LoginForm, RegistrationForm
from noveltorpedo.forms import SearchForm
from haystack.views import SearchView as HaystackSearchView


def login(request):
    form = LoginForm()
    # Needs to implement logic for handling logins
    return render(request, 'noveltorpedo/login.html', {'form': form})


def logout(request):
    # Needs to be implemented
    return HttpResponse("This page will log you out in the future.")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Creates a new user upon valid input.
            form.save()
            return HttpResponse("Registration successful.")
    else:
        form = RegistrationForm()
    return render(request, 'noveltorpedo/register.html', {'form': form})


class SearchView(HaystackSearchView):
    def __init__(self, template=None, load_all=True, searchqueryset=None):
        self.form_class = SearchForm
        self.results_per_page = 16

        super(self.__class__, self).__init__(template, load_all, self.form_class, searchqueryset, self.results_per_page)
