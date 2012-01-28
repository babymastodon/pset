from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date
import urllib
from django import forms
from itertools import chain

#import models and forms here
from main.models import *
from main.forms import *

#replacing the default login_required with our own
def login_required(f):
    def login_required_func(*args, **kwargs):
        if args[0].user.is_authenticated():
            return f(*args,**kwargs)
        return HttpResponseRedirect(reverse('main.account_views.login_page')+"?next="+urllib.quote(args[0].get_full_path()))
    return login_required_func
   
def all_newsfeed(request, feedtype, pk, page=1):
    rc={}
    page = int(page)
    rc['feed'] = get_newsfeed(feedtype, pk, page)
    rc['next'] = reverse('main.views_common.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page+1})
    if page>1:
        rc['prev'] = reverse('main.views_common.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page-1})
    rc['page'] = page
    rc['feed']['link'] = None
    return render(request, 'main/modules/all_newsfeed.html', rc)

def get_newsfeed(feedtype, pk, page=1):
    r={}
    r['link'] = reverse("main.views_common.all_newsfeed", kwargs={'feedtype':feedtype, 'page':0, 'pk':pk})
    r['header']="Recent Activity"
    if feedtype=="profile":
        newsfeed1 = Activity.objects.filter(target__target_type='User', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[:page*10]

        newsfeed2 = Activity.objects.filter(actor__pk=pk).order_by('-time_created')[:page*10]
        r['feed'] = sorted(chain(newsfeed1,newsfeed2),key=lambda x: x.time_created)[page*10-1:(page-1)*10--1:-1]
        n = User
    if feedtype=='class':
        r['feed'] = Activity.objects.filter(target__target_type='Class', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[(page-1)*10:page*10]
        n=Class
    if feedtype=='party':
        r['feed'] = Activity.objects.filter(target__target_type='Party', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[(page-1)*10:page*10]
        n=Party
    #get the name of the thingy
    try:
        r['name'] = n.objects.get(pk=pk).get_name()
    except Exception as e:
        pass
    return r
