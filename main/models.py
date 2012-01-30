from django.db import models
from django.contrib.auth.models import User
import urllib2, cStringIO, itertools
from django.core.files.base import ContentFile
from django.conf import settings
from django_facebook.models import FacebookProfileModel
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils import timezone
from datetime import datetime, date, timedelta
from PIL import Image
import random

#datetime to string
def time_string(t):
    return timezone.localtime(t).strftime("%I:%M%p").lstrip("0")

def day_string(t):
    return timezone.localtime(t).strftime("%b %d")

def time_ago(t):
    delta = timezone.now()-t
    if delta < timedelta(seconds=20):
        return "a few seconds ago"
    if delta < timedelta(seconds=50):
        return "thirty seconds ago"
    if delta < timedelta(minutes=1, seconds=30):
        return "one minute ago"
    if delta < timedelta(minutes=60):
        return str(delta.seconds/60) + " minutes ago"
    if delta < timedelta(minutes=100):
        return "about an hour ago"
    if delta < timedelta(hours=24):
        return str(delta.seconds/3600) + " hours ago"
    if delta < timedelta(days=1):
        return "at " + time_string(t)
    else:
        return "on " + day_string(t)


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
    def get_link(self):
        return reverse("main.class_views.class_details", kwargs={'pk': self.pk})
    def map_view(self):
        return reverse("main.search_views.parties_by_class", kwargs={'pk': self.pk})
    def get_name(self):
        return unicode(self)
    def get_image(self):
        return getattr(settings, "STATIC_URL", "static/")+"images/school.png"
    def get_linked_name(self):
        return '<a href="' + self.get_link() + '" >' + self.get_name() + "</a>"

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
    def get_image(self):
        return self.class_obj.get_image()
    def get_name(self):
        return self.get_title()
    def get_link(self):
        return reverse("main.class_views.class_details", kwargs={'pk': self.class_obj.pk})
    def get_linked_name(self):
        return '<a href="' + self.get_link() + '" >' + self.get_name() + "</a>"

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
    description = models.TextField(blank=True) #user description
    courses = models.ManyToManyField(Course, blank=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)
    department = models.CharField(max_length=100, blank=True)
    klasses = models.ManyToManyField(Class, through="UserClassData", blank=True)
    followees = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True)
    friends = models.ManyToManyField("self", blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    email_invitations = models.BooleanField(default=True)
    email_party = models.BooleanField(default=True)
    email_comment = models.BooleanField(default=True)
    private_profile = models.BooleanField(default=False)
    private_activities = models.BooleanField(default=False)
    private_comments = models.BooleanField(default=False)
    reindex = models.BooleanField(default=True)
    def __unicode__(self):
        return unicode(self.user) + "info"

    def get_title(self):
        return self.user.username

    def get_description(self):
        return self.description 
    def get_summary(self):
        s = self.get_name()
        if self.graduation_year: s += ", " + str(self.graduation_year)
        return s

    def get_meta(self):
        meta = self.user.first_name + " " + self.user.last_name
        if self.graduation_year != None:
            meta = meta + ", '" + str(self.graduation_year)
        return meta 
    
    def get_prof_pic(self):
        if self.image:
            return self.image.url
        else:
            return getattr(settings, "STATIC_URL", "static/")+"images/people.png"
    def get_image(self):
        return self.get_prof_pic()
    def get_link(self):
        return reverse("main.account_views.profile_page", kwargs={'pk': self.user.pk})
    def get_name(self):
        if self.user.first_name or self.user.last_name:
            return self.user.first_name + " " + self.user.last_name
        else:
            return self.user.username
    def get_linked_name(self):
        return '<a href="' + self.get_link() + '" >' + self.get_name() + "</a>"

#getname and get_link for the user class
User.get_name = lambda self: self.user_info.get_name()
User.get_summary = lambda self: self.user_info.get_summary()
User.get_link = lambda self: self.user_info.get_link()
User.get_prof_pic = lambda self: self.user_info.get_prof_pic()
User.get_image = lambda self: self.user_info.get_image()
User.get_linked_name = lambda self: self.user_info.get_linked_name()

class UserClassData(models.Model):
    #things like confidence
    user_info = models.ForeignKey(UserInfo)
    class_obj = models.ForeignKey(Class)
    experience = models.CharField(max_length=100, blank=True)
    instructor = models.CharField(max_length=100, blank=True)
    recitation_leader = models.CharField(max_length=100, blank=True) 

class Party(models.Model):
    class_obj = models.ForeignKey(Class)
    starttime = models.DateTimeField()
    endtime = models.DateTimeField()
    title = models.CharField(max_length=100)
    agenda = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=100, blank=True)
    building_img = models.CharField(max_length=200, blank=True)
    lat = models.CharField(max_length=20)
    lng = models.CharField(max_length=20)
    admins = models.ManyToManyField(User, related_name="party_set_admin")
    attendees = models.ManyToManyField(User, related_name="party_set_attend")
    active = models.BooleanField(default=True)
    def get_link(self):
        return reverse("main.party_views.party_details", kwargs={'pk': self.pk})
    def __unicode__(self):
        return self.title
    def get_name(self):
        return unicode(self)
    def get_image(self):
        return self.building_img
    def get_linked_name(self):
        return '<a href="' + self.get_link() + '" >' + self.get_name() + "</a>"
    def get_start_time(self):
        return time_string(self.starttime)
    def get_end_time(self):
        return time_string(self.endtime)
    def get_day(self, word=False):
        s = timezone.localtime(self.starttime)
        e = timezone.localtime(self.endtime)
        now = timezone.now()
        if s < now and now < e:
            return "Right Now!"
        if s.date() == now.date():
            return "Today"
        if s.date() - now.date() == timedelta(days=1):
            return "Tomorrow"
        if word:
            return s.strftime("%A")
        return day_string(self.starttime)
    def get_day_name(self):
        return self.get_day(word=True)

class Invitation(models.Model):
    sender = models.ForeignKey(User, related_name="sent_invitations")
    invitee = models.ForeignKey(User, related_name="recieved_invitations")
    party = models.ForeignKey(Party)

def create_hash():
    return "%032x" % random.getrandbits(128)

class PendingHash(models.Model):
    user = models.ForeignKey(User)
    party = models.ForeignKey(Party, null=True)
    hashcode = models.CharField(max_length=100)
    @staticmethod
    def create(user):
        h1 = create_hash()
        ph = PendingHash(user=user, hashcode=h1)
        ph.save()
        return ph

class InviteHash(models.Model):
    party = models.ForeignKey(Party)
    hashcode = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    @staticmethod
    def create(party, email):
        h = create_hash()
        ih = InviteHash(party=party, email=email, hashcode = h)
        ih.save()
        return ih
    def get_invite_link(self):
        return reverse('main.account_views.invite_hashcode', kwargs={'hashcode': self.hashcode, 'pk':self.party.pk})


class DummyTarget(models.Model):
    def get_name(self):
        return "Dum Dum"
    get_link = get_name
    get_linked_name = get_name

target_types = [(a,a) for a in ['User','Class','Party']]
target_dict = {'User':User, 'Class':Class, 'Party':Party, 'DummyTarget':DummyTarget}
class Target(models.Model):
    target_id = models.IntegerField()
    target_type = models.CharField(max_length=20)
    def get_name(self):
        return target_dict[self.target_type].objects.get(pk=self.target_id).get_name()
    def get_link(self):
        return target_dict[self.target_type].objects.get(pk=self.target_id).get_link()
    def get_linked_name(self):
        return '<a href="' + self.get_link() + '" >' + self.get_name() + "</a>"
    def admins(self):
        if self.target_type=='Party':
            return Party.objects.get(pk=self.target_id).admins.all()
        elif self.target_type=='User':
            return [User.objects.get(pk=self.target_id)]
        return []
    def __unicode__(self):
        return self.target_type + ": " + self.get_name()

activity_types = [(a,a) for a in ['comment','created','attending','edited', 'joined', 'newaccount']]
class Activity(models.Model):
    activity_type = models.CharField(max_length=20, choices=activity_types)
    actor = models.ForeignKey(User)
    target = models.OneToOneField(Target)
    time_created = models.DateTimeField(auto_now_add=True)
    def get_linked_actor(self):
        return '<a href="' + self.actor.user_info.get_link() + '" >' + self.actor.user_info.get_name() + '</a>'
    def get_icon(self):
        static = getattr(settings, "STATIC_URL", "static/")+"images/css/icons/"
        if self.activity_type=="comment":
            return static + 'commentblack32.png'
        elif self.activity_type=='created':
            return static + 'glitter32.png'
        elif self.activity_type == 'attending':
            return static + 'userplus32.png'
        elif self.activity_type=='edited':
            return static + 'pencil32.png'
        elif self.activity_type=='joined':
            return static + 'mapleleaf32.png'
        elif self.activity_type=='newaccount':
            return static + 'glitter32.png'
    def get_content(self):
        if self.activity_type=="comment":
            return self.get_linked_actor() + " left a comment at " + self.target.get_linked_name()
        elif self.activity_type=='created':
            return self.get_linked_actor() + " is hosting " + self.target.get_linked_name()
        elif self.activity_type=='edited':
            return self.get_linked_actor() + " updated " + self.target.get_linked_name()
        elif self.activity_type=='attending':
            return self.get_linked_actor() + " is attending " + self.target.get_linked_name()
        elif self.activity_type=='joined':
            return self.get_linked_actor() + " added " + self.target.get_linked_name()
        elif self.activity_type=='newaccount':
            return self.get_linked_actor() + " joined InTheLoop!"
    def get_time(self):
        return time_ago(self.time_created)
    def get_actor(self):
        return str(self.actor)
    @staticmethod
    def create(activity_type, actor, target=None):
        if not target:
            dummies = DummyTarget.objects.all()
            if not dummies:
                target = DummyTarget()
                target.save()
            else:
                target=dummies[0]
        t = Target(target_id=target.pk, target_type=target.__class__.__name__)
        t.save()
        a = Activity(activity_type=activity_type, actor=actor, target=t)
        a.save()
        return a
    def __unicode__(self):
        return str(self.actor) + " " + self.activity_type + " " + str(self.target)

class Comment(models.Model):
    comment = models.TextField()
    actor = models.ForeignKey(User)
    target = models.OneToOneField(Target)
    time_created = models.DateTimeField(auto_now_add=True)
    def get_image(self):
        return self.actor.user_info.get_prof_pic()
    def get_time(self):
        return time_ago(self.time_created)
    def get_linked_actor(self):
        return '<a href="' + self.actor.user_info.get_link() + '" >' + self.actor.user_info.get_name() + '</a>'
    @staticmethod
    def create(comment, actor, target):
        t = Target(target_id=target.pk, target_type=target.__class__.__name__)
        t.save()
        a = Comment(comment=comment, actor=actor, target=t)
        a.save()
        Activity.create(actor=actor, activity_type="comment", target=target)
        return a
    def __unicode__(self):
        return str(self.actor) + " comment to " + str(self.target)
    def can_delete(self,user):
        return (user==self.actor) or (user in self.target.admins()) or user.is_staff

