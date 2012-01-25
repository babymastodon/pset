from django.db import models
from django.contrib.auth.models import User
import urllib2, cStringIO, itertools, datetime
from django.core.files.base import ContentFile
from django_facebook.models import FacebookProfileModel

def resize_dimensions(width, height, longest_side):
    if width>height and width>longest_side:
        width,height = (longest_side, height*longest_side//width)
    elif height>width and height>longest_side:
        width,height = (width*longest_side//height, longest_side)
    return(width, height)

def resize_image(i,dim=400, w=None, h=None):
    if not i:
        return ""
    imagefile  = cStringIO.StringIO(i.read())
    imageImage = Image.open(imagefile)

    (width, height) = imageImage.size
    if w:
        (width, height) = (w, float(height)/width*w)
    elif h:
        (width, height) = (float(width)/height*h, h)
    else:
        (width, height) = resize_dimensions(width, height, dim)
    
    resizedImage = imageImage.resize((width, height), Image.ANTIALIAS)
    imagefile = cStringIO.StringIO()
    resizedImage.save(imagefile,'JPEG',quality=85)
    return ContentFile(imagefile.getvalue())

# Create your models here.
class Picture(models.Model):
    sequence = models.IntegerField(default=10) #sequence number in case their order needs to change
    thumbnail300 = models.ImageField(upload_to='%y/%m/thm300')
    thumbnail150 = models.ImageField(upload_to='%y/%m/thm150')
    image = models.ImageField(upload_to='%y/%m/img/',blank=True)
    link = models.CharField(max_length=1000,blank=True)
    def getUrl():
        if link:
            return link
        if image:
            return image.storage.url()
        return ""
    def uploadImage(page, image):
        thm300 = resize_image(image,width=300)
        thm150 = resize_image(image,width=150)
        return Picture(image=image, thumbnail300=thm300, thumbnail150=thm150, page=page)
    def downloadImage(page, url):
        u = urllib2.urlopen(url)
        data = u.read()
        u.close()
        return Picture.uploadImage(page,ContentFile(data))
    def linkImage(page, url):
        u = urllib2.urlopoen(url)
        data = cStringIO.StringIO(u.read())
        u.close()
        thm300 = resize_image(data,width=300)
        thm150 = resize_image(data,width=150)
        return Picture(link=url, thumbnail300=thm300, thumbnail150=thm150)

class Resource(models.Model):
    sequence = models.IntegerField(default=10) #sequence number in case order needs to change
    file = models.FileField(upload_to='%y/%m/file',blank=True)
    link = models.CharField(max_length=1000,blank=True)
    def getUrl():
        if link:
            return link
        if file:
            return file.storage.url()
        return ""

class Course(models.Model):
    number = models.CharField(max_length=5)

class Class(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_meta(self):
        return list(self.classnumber_set.all())

    def __unicode__(self):
        return unicode(self.title)

class ClassNumber(models.Model):
    number = models.CharField(max_length=20)
    class_obj = models.ForeignKey(Class, null=True)#default related name is classnumber_set

    def get_title(self):
        return self.number + " " + self.class_obj.title

    def get_description(self):
        return self.class_obj.description

    def get_meta(self):
        return list(self.class_obj.classnumber_set.all())

    def __unicode__(self):
        return unicode(self.number)

"""
    about_me = models.TextField(blank=True)
    facebook_id = models.BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(
        blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
        upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    raw_data = models.TextField(blank=True)
"""
class UserInfo(FacebookProfileModel):
    user = models.OneToOneField(User, related_name="user_info")
    description = models.TextField() #user description
    courses = models.ManyToManyField(Course)
    graduation_year = models.IntegerField(blank=True, null=True)
    current_classes = models.ManyToManyField(Class, through="UserClassData")
    friends = models.ManyToManyField("self")

    def __unicode__(self):
        return str(self.user) + " info"
   
    def get_title(self):
        return self.user.username

    def get_description(self):
        return self.description 

    def get_meta(self):
        meta = self.user.first_name + " " + self.user.last_name
        if self.graduation_year != None:
            meta = meta + ", '" + self.graduation_year
        return meta 

class UserClassData(models.Model):
    #things like confidence
    userinfo = models.ForeignKey(UserInfo)
    _class = models.ForeignKey(Class)

class Party(models.Model):
    class_obj = models.ForeignKey(Class)
    starttime = models.TimeField()
    endtime = models.TimeField()
    day = models.DateField()
    title = models.CharField(max_length=30)
    agenda = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=10, blank=True)
    building_img = models.CharField(max_length=200, blank=True)
    lat = models.CharField(max_length=20)
    lng = models.CharField(max_length=20)
    admins = models.ManyToManyField(User, related_name="admin_set")
    attendees = models.ManyToManyField(User, related_name="attendee_set")
    active = models.BooleanField(default=True)
    
class PendingHash(models.Model):
    user = models.ForeignKey(User)
    party = models.ForeignKey(Party, null=True)
    hashcode = models.CharField(max_length=100)

