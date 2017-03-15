from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect, HttpResponse
from noveltorpedo.forms import RegistrationForm, SearchForm, TumblrAddForm
from haystack.views import SearchView as HaystackSearchView


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Creates a new user upon valid input.
            user = form.save()

            # Login this new user automatically.
            auth_login(request, user)
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'noveltorpedo/auth/register.html', {'form': form})


def submit_story_tumblr(request):
    if request.method == "POST":
        form = TumblrAddForm(request.POST)
        if form.is_valid():
            form.save()
            #return HttpResponse("Story submitted successfully.")
            return render(request, 'noveltorpedo/submit-tumblr.html', {'form': form, 'success': "Story submitted successfully."})
    else:
        form = TumblrAddForm()

    return render(request, 'noveltorpedo/submit-tumblr.html', {'form': form})


class SearchView(HaystackSearchView):
    def __init__(self, template=None, load_all=True, searchqueryset=None):
        self.form_class = SearchForm
        self.results_per_page = 16

        super(self.__class__, self).__init__(template, load_all, self.form_class, searchqueryset, self.results_per_page)
