from django import forms
from main.models import *
from userena.forms import SignupForm, SignupFormOnlyEmail

#Make forms here

class PictureFileForm(forms.ModelForm):
    class Meta:
        model=Picture
        fields=('image',)
    def create(self,page):
        return Picture.uploadImage(page, self.cleaned_data['image'])

class PictureLinkForm(forms.ModelForm):
    class Meta:
        model=Picture
        fields=('link',)
    def create(self,page):
        return Picture.linkImage(page, self.cleaned_data['link'])

class LinkForm(forms.ModelForm):
    class Meta:
        model=Resource
        fields=('link',)
    def create(self,page):
        return Resource(page=page, link=self.cleaned_data['link'])

class FileForm(forms.ModelForm):
    class Meta:
        model=Resource
        fields=('file',)
    def create(self,page):
        return Resource(page=page,file=self.cleaned_data['file'])

class EmailRegisterForm(forms.Form):
    email = forms.EmailField()
    pw1 = forms.CharField(widget=forms.PasswordInput, label='Password:')
    pw2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password:')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']
class PartyCreateForm(forms.Form):
    klass = forms.CharField(max_length=100)
    title = forms.CharField(max_length=100)
    day = forms.DateField()
    start_time = forms.TimeField(input_formats=valid_time_formats)
    end_time = forms.TimeField(input_formats=valid_time_formats)
    agenda = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    room = forms.CharField(max_length=100)
    lat = forms.CharField(max_length=100)
    lng = forms.CharField(max_length=100)
    location_data = forms.CharField()#the json from the whereis request

