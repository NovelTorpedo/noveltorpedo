from haystack import indexes
from noveltorpedo.models import Story as StoryModel


class Story(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')

    def get_model(self):
        return StoryModel
