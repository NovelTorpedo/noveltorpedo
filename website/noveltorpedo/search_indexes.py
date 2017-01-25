from haystack import indexes
from noveltorpedo.models import Story


class StoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    contents = indexes.CharField(model_attr='contents')

    def get_model(self):
        return Story