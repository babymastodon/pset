from django import forms
from main.models import *

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
    pw1 = forms.CharField(widget=forms.PasswordInput)
    pw2 = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

