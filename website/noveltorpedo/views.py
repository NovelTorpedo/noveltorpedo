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
            if form.save():
                return render(request, 'noveltorpedo/submit-tumblr.html',
                              {'form': form, 'message': "Story submitted successfully."})
            else:
                return render(request, 'noveltorpedo/submit-tumblr.html',
                              {'form': form, 'message': "There was an error fetching that story."})
    else:
        form = TumblrAddForm()

    return render(request, 'noveltorpedo/submit-tumblr.html', {'form': form})


class SearchView(HaystackSearchView):
    def __init__(self, template=None, load_all=True, searchqueryset=None):
        self.form_class = SearchForm
        self.results_per_page = 16

        super(self.__class__, self).__init__(template, load_all, self.form_class, searchqueryset, self.results_per_page)
