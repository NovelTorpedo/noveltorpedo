from haystack.forms import SearchForm as HaystackSearchForm


class SearchForm(HaystackSearchForm):
    def __init__(self, *args, **kwargs):
        super(SearchForm).__init(self, *args, **kwargs)
