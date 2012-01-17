#!/usr/bin/python

import os
import sys
sys.path.append('/var/www/pset')
os.environ['DJANGO_SETTINGS_MODULE'] = 'pset.settings'

from django.core.management import setup_environ
from pset import settings
setup_environ(settings)

from main.models import *
import urllib2, re, time,pprint, copy

def name_range(a,b):
    if not b:
        return [a]
    prefix = a[:-2]
    suffix1 = int(a[-2:])
    suffix2 = int(b[-2:])
    tmp=[]
    for i in range(suffix1, suffix2+1):
        suffix = ("0"+str(i))[-2:]
        new_number = prefix+suffix
        tmp.append(new_number)
    return tmp

#first get the list of all of the courses offered
url="http://student.mit.edu/catalog/search.cgi?search=&style=verbatim"
page = urllib2.urlopen(url).read()
lines = re.findall(r'<DT><A HREF="([^"]*)">([^\s]*)\s([^<]*)',page)

#next get the list of all of the pages with the details of the courses offered
cat_url="http://student.mit.edu/catalog/"
detail_pages={}
for l in lines:
    detail_pages[l[0].split("#")[0]]=""

#now get and parse all of the detailed course descriptions, making note of classes listed under multiple names (like the ones with numbers endign in J)
courses=[]
for p in detail_pages:
    try:
        page = urllib2.urlopen(cat_url+p).read()
        #first regex finds the table
        s = re.compile(r'<table border=0.*?</table>',re.MULTILINE|re.DOTALL)
        table = s.search(page).group(0)
        #apparently puttin capture groups inside capture groups doesn't work, so the remaining regex must be applied in sequence
        r = re.compile(r'\n(?=<a n)')#grabs the entire block
        t = re.compile(r'^(?:<p>)?<h3>(?P<num1>\w+\.\w+)(?P<optional>\s?-?,?\s?\w+\.\w+)?\s?(?P<title>.*)$', re.M)#grabbs the line with the title
        t2 = re.compile(r'(\w+\.\w+)')#grabs the second number
        an = re.compile(r'<a name="([^"]*)"></a>')
        d = re.compile(r'f">[\r\n]+<br>([^<]*)$', re.M)#gets the description
        s = re.compile(r'<br>\(Same.*\)')#gets the related classes
        ss = re.compile(r'<br>\(Subject.*\)')#gets more related classes
        sss = re.compile(r'<br>Credit c.*')#gets the un-related classes
        s2 = re.compile(r'\w+\.\w+')#splits the related classes
        n=0
        for m in r.split(table)[1:]:
            moo = {}
            tmp = t.search(m)
            if tmp:
                tmp = tmp.groupdict()
                moo['title']=tmp['title']
                moo['numbers']= an.findall(m)
                tmp = d.search(m)
                if not tmp:
                    moo['description']=""
                else:
                    moo['description']=tmp.group(1)
                tmp = s.search(m)
                if tmp:
                    for a in s2.findall(tmp.group(0)):
                        if 'html' not in a:
                            moo['numbers'].append(a)
                tmp = ss.search(m)
                if tmp:
                    for a in s2.findall(tmp.group(0)):
                        if 'html' not in a:
                            moo['numbers'].append(a)
                tmp = sss.search(m)
                moo['not_related']=[]
                if tmp:
                    for a in s2.findall(tmp.group(0)):
                        if 'html' not in a:
                            moo['not_related'].append(a)
                moo['numbers']=list(set([x[:-1] if x[-1]=='J' else x for x in moo['numbers']])) #remove duplicates
                moo['not_related']=list(set([x[:-1] if x[-1]=='J' else x for x in moo['not_related']])) #remove duplicates
                moo['not_related']=[x for x in moo['not_related'] if x not in moo['numbers']] #remove from not_related if it is indeed in the relaed list of classes
                courses.append(moo)
    except urllib2.HTTPError:
        pass

#generated dicts of sets for related and unrelated:
unrelated={}
for c in courses:
    for n in c['numbers']+c['not_related']:
        unrelated[n]=set()
for c in courses:
    for n in c['numbers']:
        for m in c['not_related']:
            unrelated[n].add(m)

#first loop through the database ensures that all of the course numbers have been created
for c in courses:
    for d in c['numbers']:
        obs2 = ClassNumber.objects.filter(number=d)
        print "Checking number: " + d
        if not obs2.exists():
            ob2 = ClassNumber(number=d)
            ob2.save()
            print "Creating new: " + ob2.number
    print "Processed: " + c['title']

updated = {}

def update_ob_with_class(dic, cl):
    flag=False
    if len(cl.title)<len(dic['title']):
        cl.title=dic['title']
        flag=True
    if len(cl.description)<len(dic['description']):
        cl.description=dic['description']
        flag=True
    if flag: cl.save()
    for d in dic['numbers']:
        if d not in updated:
            ob2 = ClassNumber.objects.get(number=d)
            if ob2._class != cl:
                print "Linking " + str(ob2.number) + " to class " + cl.title
                ob2._class = cl
                ob2.save()
                updated[d]=True

#second loop through the database creates the actual classes and links them to their numbers
for c in courses:
    up=False#check to see if all of the elements have already been updated
    for b in c['numbers']:
        if b not in updated:
            up=True
    if up:#if there is a number in our list that need to be updated
        found_neighbor=False
        for b in c['numbers']:#try to find a neighbor that already has a class
            ob2 = ClassNumber.objects.get(number=b)
            if ob2._class:
                print "Found related classname with class: " + ob2.number
                found_neighbor=True
                update_ob_with_class(c,ob2._class)
                break;
        if not found_neighbor:
            #no neighbors had a class, first search for a class with the same name
            cl = Class.objects.filter(title=c['title'])
            found_class=False
            #we only want to attach to this class if it doesn't have any titles that are in our not_related list
            for single_class in list(cl):
                if not [x for x in list(single_class.classnumber_set.all()) if x.number in [d for a in c['numbers'] for d in unrelated[a]]]: #if the intersection of the lists is empty
                    update_ob_with_class(c,single_class)
                    found_class=True
            #if no class already has that name, make new class
            if not found_class:
                cl = Class()
                print "Created class for: " + str(c['title'])
                update_ob_with_class(c, cl)

print "Done"
