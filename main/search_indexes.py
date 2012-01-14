from haystack import indexes
from main.models import *


class courseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(VideoIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_model(self):
        return Course
    
    def should_update(self, instance, **kwargs):
        if True:
            return True
        else:
            self.remove_object(instance, **kwargs)
            return False    

class userIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    courses = indexes.MultiValueField(indexed=True, stored=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(VideoIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def prepare_courses(self, obj):
        return [str(s) for s in obj.user_info.courses.all()]

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_model(self):
        return User
    
    def should_update(self, instance, **kwargs):
        if True:
            return True
        else:
            self.remove_object(instance, **kwargs)
            return False     
