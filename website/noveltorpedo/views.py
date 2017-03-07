from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from noveltorpedo.forms import RegistrationForm
from noveltorpedo.forms import SearchForm
from noveltorpedo.forms import TumblrAddForm
from haystack.views import SearchView as HaystackSearchView


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

def submit_story_tumblr(request):
    if request.method == "POST":
        form = TumblrAddForm(request.POST)
        if form.is_valid():
            form.clean_name()
            form.save()
            return HttpResponse("Stories from submitted successfully.")
    else:
        form = TumblrAddForm()

    return render(request, 'noveltorpedo/submit.html', {'form': form})

class SearchView(HaystackSearchView):
    def __init__(self, template=None, load_all=True, searchqueryset=None):
        self.form_class = SearchForm
        self.results_per_page = 16

        super(self.__class__, self).__init__(template, load_all, self.form_class, searchqueryset, self.results_per_page)
