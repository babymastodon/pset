from haystack import indexes
from main.models import *
import string

class ClassIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(ClassIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_model(self):
        return Class
    
    def should_update(self, instance, **kwargs):
        if True:
            return True
        else:
            self.remove_object(instance, **kwargs)
            return False    

class ClassNumberIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(ClassNumberIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def prepare_text(self, obj):
        return obj.number + " " + obj.class_obj.title

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_model(self):
        return ClassNumber
    
    def should_update(self, instance, **kwargs):
        if True:
            return True
        else:
            self.remove_object(instance, **kwargs)
            return False    

class UserInfoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    courses = indexes.MultiValueField(indexed=True, stored=True)
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(UserInfoIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def prepare_courses(self, obj):
        return [str(s) for s in obj.courses.all()]

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(user__is_active=True)

    def get_model(self):
        return UserInfo
    
    def should_update(self, instance, **kwargs):
        if True:
            return True
        else:
            self.remove_object(instance, **kwargs)
            return False     
