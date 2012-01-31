from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date
from django import forms
import simplejson

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def all_attending(request, pk):
    rc={}
    rc['attendees'] = get_all_attending(request, pk)
    rc['title']= 'All Attending'
    return render_to_response("main/modules/people_popup.html", rc, context_instance=RequestContext(request))

def all_followers(request, pk):
    rc={}
    rc['attendees'] = get_followers(request, pk)
    rc['title']= 'All Followers'
    return render_to_response("main/modules/people_popup.html", rc, context_instance=RequestContext(request))

def all_followees(request, pk):
    rc={}
    rc['attendees'] = get_followees(request, pk)
    rc['title']= 'All Followees'
    return render_to_response("main/modules/people_popup.html", rc, context_instance=RequestContext(request))

def get_followees(request, pk):
    user = get_object_or_404(User, pk=pk)
    if (not user.user_info.private_profile) or request.user.is_authenticated():
        return user.user_info.followees.all()
    return []

def get_followers(request, pk):
    user = get_object_or_404(User, pk=pk)
    if (not user.user_info.private_profile) or request.user.is_authenticated():
        return user.user_info.followers.all()
    return []

def get_all_attending(request, pk):
    party = get_object_or_404(Party, pk=pk)
    attendees = party.attendees.all()
    return attendees

def follow(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = User.objects.filter(pk=pk)
    if c:
        request.user.user_info.followees.add(c[0].user_info)
        request.user.user_info.save()
        return {'status':'success'}
    return {'status': 'person does not exist'}

def unfollow(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = User.objects.filter(pk=pk)
    if c:
        request.user.user_info.followees.remove(c[0].user_info)
        return {'status':'success'}
    return {'status': 'person does not exist'}

def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        pk = request.REQUEST.get('pk',None)
        if pk:
            pk=int(pk)
        if verb=='follow':
            result = follow(request, pk)
        elif verb=='unfollow':
            result = unfollow(request, pk)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")
