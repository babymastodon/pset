#!/usr/bin/python

import os
import sys
sys.path.append('/var/www/pset')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pset.settings'

from django.core.management import setup_environ
from pset import settings
setup_environ(settings)

from main.models import *
from django.contrib.auth.models import User
from main.account_views import *
import urllib2, re, time,pprint, copy, random, simplejson, urllib
from django.utils import timezone
from datetime import datetime, date, timedelta
import time

names = open('names.txt','r')
ddd = {}
for a in names:
    l = [a.rstrip(",") for a in a.split()] + [""]
    first, last = l[0], l[1]
    username = (first+last).lower()
    ddd[username] = {'first':first, 'last':last}

numclasses = ClassNumber.objects.all().count()
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

favorites = open("favorites.txt","r").read().split('\n')
activities = open("activities.txt","r").read().split('\n')
items = [x.rstrip('s') for x in open("items.txt","r").read().split('\n')]
adjectives = open("adjectives.txt","r").read().split('\n')
food_adjectives = open("food_adjectives.txt","r").read().split('\n')
food = open("food.txt","r").read().split('\n')

lngy = -71.10533209468258
laty = 42.35790098687922
lngo = -71.10267134333981
lato = 42.354285678498044
lngx = -71.08361693049801
latx = 42.360437921203044

dy = [lngy-lngo, laty-lato]
dx = [lngx-lngo, latx-lato]

for u in ddd:
    u = createAccount(email=u+"@babymastodon.com", username=u, first_name=ddd[u]['first'], last_name=ddd[u]['last'], password="moo")
    Activity.create(actor=u, activity_type='newaccount')
numpeople = User.objects.all().count()

for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #add classes
        for i in range(0,5):
            pk = random.randint(0,300)
            c = Class.objects.filter(pk=pk)
            if c:
                c=c[0]
                UserClassData(user_info = u.user_info, class_obj = c).save()
                Activity.create('joined',u,c)
                print "linked " + u.get_name() + " to " + c.get_name()

for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #grad year and course
        n = random.randint(0,len(department_choices)-1)
        y = random.randint(2012, 2016)
        u.user_info.department=department_choices[n]
        u.user_info.graduation_year=y
        u.user_info.save()

for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #create bio
        a = random.randint(0,len(favorites)-1)
        b = random.randint(0,len(activities)-1)
        c = random.randint(0,len(items)-1)
        u.user_info.bio = "I am a " + items[c] + ". In my free time I like to do " + activities[b] + ". My favorite word is " + favorites[a] + "."
        u.user_info.save()


for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #random followers and followees
        for i in range(0,3):
            pk = random.randint(0,numpeople-1)
            f = User.objects.filter(pk=pk)
            if f:
                f=f[0]
                u.user_info.followees.add(f.user_info)
                u.user_info.save()

for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #create parties
        now = timezone.now()
        hour = timedelta(hours=2)
        if random.randint(0,3)==3:
            klasses = u.user_info.klasses.all()
            klass = klasses[random.randint(0, klasses.count()-1)]
            number = klass.get_meta()[0].number
            
            f = food[random.randint(0,len(food)-1)]
            fa = food_adjectives[random.randint(0,len(food_adjectives)-1)]
            a = adjectives[random.randint(0,len(adjectives)-1)]
            
            x = random.uniform(0,1)
            y = random.uniform(0,1)
            
            lng = lngo + x * dx[0] + y * dy[0]
            lat = lato + x * dx[1] + y * dy[1]
            
            minutes = random.randint(0,10080)
            delta = timedelta(minutes=minutes)
            
            query={}
            query['type'] = 'coord'
            query['output'] = 'json'
            query['q'] = str(lng) + "," + str(lat)
            url = "http://whereis.mit.edu/search?"+urllib.urlencode(query)
            webpage = urllib.urlopen(url)
            data = webpage.read()
            webpage.close()
            d = simplejson.loads(data)
            name = "Mystery Building"
            pict = "http://web.mit.edu/campus-map/objimgs/object-7.thumb.jpg"
            if d:
                d = d[0]
                if 'name' in d:
                    name = d['name']
                if 'bldgimg' in d:
                    pict = d['bldgimg']
            
            party = Party()
            party.starttime = now+delta
            party.endtime = now+delta+hour
            party.title = (a + " party for " + number).title()
            party.agenda = "Pset " + str(random.randint(0,15)) + " while eating free " + fa + " " + f
            
            party.location = name
            party.room = str(random.randint(0,1000))
            party.lat = str(lat)
            party.lng = str(lng)
            party.building_img = pict
            party.class_obj = klass
            party.save()
            UserPartyTable(user=u, party=party).save()
            party.admins.add(u)
            party.save()
            Activity.create(actor=u, activity_type="created", target=party)
            print party.get_name()
            #var = raw_input()
            time.sleep(1)

for u in ddd:
    u = User.objects.filter(username = u)
    if u:
        u=u[0]
        #join parties
        for k in u.user_info.klasses.all():
            for p in k.party_set.all():
                count = p.attendees.all().count()
                if count<7:
                    if not UserPartyTable.objects.filter(user=u, party=p).exists():
                        UserPartyTable(user=u, party=p).save()
                        Activity.create(actor=u, activity_type="attending", target=p)
