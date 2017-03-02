from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from noveltorpedo.forms import SearchForm
from haystack.views import SearchView as HaystackSearchView


def register(request):
    template = loader.get_template('noveltorpedo/register.html')
    return HttpResponse(template.render(None, request))


class SearchView(HaystackSearchView):
    def __init__(self, template=None, load_all=True, searchqueryset=None):
        self.form_class = SearchForm
        self.results_per_page = 16

        super(self.__class__, self).__init__(template, load_all, self.form_class, searchqueryset, self.results_per_page)
