from django.db import models
from django.contrib.auth.models import User
import urllib2, cStringIO, itertools, datetime
from django.core.files.base import ContentFile

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
        return list(self.class_obj.classnumber_set.exclude(pk=self.pk))

    def __unicode__(self):
        return unicode(self.number)

class UserInfo(models.Model):
    user = models.OneToOneField(User, related_name="user_info")
    profile_picture = models.OneToOneField(Picture, related_name="user_info", blank=True)
    description = models.TextField() #user description
    facebook_id = models.CharField(blank=True, max_length=100) #facebook id etc
    courses = models.ManyToManyField(Course)
    graduation_year = models.IntegerField()
    current_classes = models.ManyToManyField(Class, through="UserClassData")
    friends = models.ManyToManyField("self")

    def __unicode__(self):
        return str(self.user) + " info"

class UserClassData(models.Model):
    #things like confidence
    userinfo = models.ForeignKey(UserInfo)
    _class = models.ForeignKey(Class)

class PendingHash(models.Model):
    user = models.ForeignKey(User)
    hashcode = models.CharField(max_length=100)

class Party(models.Model):
    courses = models.ManyToManyField(Course)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    title = models.CharField(max_length=30)
    description = models.TextField()
    #location?
    #icon for map?? color?
    admins = models.ManyToManyField(User, related_name="admin_set")
    attendees = models.ManyToManyField(User, related_name="attendee_set")
