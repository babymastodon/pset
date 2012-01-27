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
from django.utils import timezone

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *
from main.search_views import get_parties_by_class

def class_details(request, pk):
    rc={}
    klass = get_object_or_404(Class,pk=pk)
    rc['class'] = klass
    rc['newsfeed'] = Activity.objects.filter(target__target_type='Class', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[:10]
    rc['comments']={'pk':pk, 'target':"Class"}
    if request.user.is_authenticated():
        rc['joined'] = request.user.user_info in klass.userinfo_set.all()
    parties = get_parties_by_class(request, pk).get('result_list',[])
    rc['num_parties'] = len(parties)
    rc['party_list'] = simplejson.dumps(parties)
    return render_to_response("main/class/class_details.html", rc, context_instance=RequestContext(request))

def class_file_upload(request):
    rc={}
    return render_to_response("main/class/file_upload.html", rc, context_instance=RequestContext(request))

def add_class(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = Class.objects.filter(pk=pk)
    if c:
        request.user.user_info.klasses.add(c[0])
        request.user.user_info.save()
        if not Activity.objects.filter(target__target_type='Class', activity_type='joined', actor=request.user, target__target_id=c[0].pk).exists():
            Activity.create('joined',request.user,c[0])
        return {'status':'success'}
    return {'status': 'class does not exist'}

def drop_class(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = Class.objects.filter(pk=pk)
    if c:
        request.user.user_info.klasses.remove(c[0])
        return {'status':'success'}
    return {'status': 'class does not exist'}

def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        pk = request.REQUEST.get('pk',None)
        if pk:
            pk=int(pk)
        if verb=='add_class':
            result = add_class(request, pk)
        elif verb=='drop_class':
            result = drop_class(request, pk)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")
