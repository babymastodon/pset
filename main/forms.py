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
    email = forms.EmailField(label="MIT Email")
    pw1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    pw2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class AddClassForm(forms.Form):
    user_info = forms.CharField(max_length=100, required=True)
    class_obj = forms.CharField(max_length=100, required=True)
    instructor = forms.CharField(max_length=100, required=False)
    recitation_leader = forms.CharField(max_length=100, required=False)
    experience = forms.CharField(max_length=100, required=False)

valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']
class PartyCreateForm(forms.Form):
    klass = forms.CharField(max_length=100, required=True)
    title = forms.CharField(max_length=100, required=True)
    day = forms.DateField(required=True)
    start_time = forms.TimeField(input_formats=valid_time_formats, required=True)
    end_time = forms.TimeField(input_formats=valid_time_formats, required=True)
    agenda = forms.CharField(max_length=100, required=True)
    location = forms.CharField(max_length=100, required=True)
    room = forms.CharField(max_length=100, required=True)
    lat = forms.CharField(max_length=100)
    lng = forms.CharField(max_length=100)
    building_img = forms.CharField()#the json from the whereis request
    #copied from above
    email = forms.EmailField(label="MIT Email", required=False)
    pw1 = forms.CharField(widget=forms.PasswordInput, label='Password', required=False)
    pw2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=False)
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

#copy/pasted from the mit website
department_choices=["Architecture (Course 4)",
        "Media Arts and Sciences (MAS)",
        "Urban Studies and Planning (Course 11)",
        "Aeronautics and Astronautics (Course 16)",
        "Biological Engineering (Course 20)",
        "Chemical Engineering (Course 10)",
        "Civil and Environmental Engineering (Course 1)",
        "Electrical Engineering and Computer Science (Course 6)",
        "Engineering Systems Division (ESD)",
        "Materials Science and Engineering (Course 3)",
        "Mechanical Engineering (Course 2)",
        "Nuclear Science and Engineering (Course 22)",
        "Anthropology (Course 21A)",
        "Comparative Media Studies (CMS)",
        "Economics (Course 14)",
        "Foreign Languages and Literatures (Course 21F)",
        "History (Course 21H)",
        "Humanities (Course 21)",
        "Linguistics and Philosophy (Course 24)",
        "Literature (Course 21L)",
        "Music and Theater Arts (Course 21M)",
        "Political Science (Course 17)",
        "Science, Technology, and Society (STS)",
        "Writing and Humanistic Studies (Course 21W)",
        "Management (Course 15)",
        "Biology (Course 7)",
        "Brain and Cognitive Sciences (Course 9)",
        "Chemistry (Course 5)",
        "Earth, Atmospheric, and Planetary Sciences (Course 12)",
        "Mathematics (Course 18)",
        "Physics (Course 8)",
        "Harvard-MIT Division of Health Sciences and Technology (HST)"]
department_tuples = [(a,a) for a in department_choices]

class UserBioForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    department = forms.ChoiceField(required=False, choices=department_tuples)
    graduation_year = forms.CharField(max_length=100, required=False, label="Class year")
    bio = forms.CharField(max_length=500, required=False)
    pic = forms.ImageField(required=False)
