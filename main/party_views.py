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
import simplejson, string

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def party_details(request, pk):
    rc={}
    return render_to_response("main/party/party_details.html", rc, context_instance=RequestContext(request))

def party_create(request):
    rc={}
    return render_to_response("main/party/party_create.html", rc, context_instance=RequestContext(request))

def party_registered(request, pk):
    rc={}
    rc['event_name']='MOOMOMOO'
    rc['event_location']="Building 35"
    rc['event_time']="Monday, December 25 at 11:30pm"
    rc['title']="Let the games begin!"
    rc['pk']=pk
    return render_to_response("main/party/party_registered.html", rc, context_instance=RequestContext(request))
    

#ajax handler for handling party update information and party delete
def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        party_pk = request.REQUEST.get('pk',None)
        if verb=='isregistered':
            result = {"status": "success", "attending":False}
        elif verb=='get_attend_button':
            return render_to_response('main/party/attend_button.html',{'pk':party_pk})
        elif verb=='register':
            result={"status": "success", 'registered':True,'link':reverse('main.party_views.party_registered',kwargs={'pk':party_pk})} 
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

