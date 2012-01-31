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
from main.people_views import *
from main.search_views import get_parties_by_class

def class_details(request, pk):
    rc={}
    klass = get_object_or_404(Class,pk=pk)
    rc['class'] = klass
    rc['comments']={'pk':pk, 'target':"Class"}
    if request.user.is_authenticated():
        rc['joined'] = request.user.user_info in klass.userinfo_set.all()
    rc['newsfeed'] = get_newsfeed(request,'class', pk)
    parties = get_parties_by_class(request, pk).get('result_list',[])
    rc['num_parties'] = len(parties)
    rc['party_list'] = simplejson.dumps(parties)
    members = get_members(request, pk)
    l = len(members)
    rc['members'] = {'header':str(l) + " Member" + ("s" if l!=1 else ""), 'list':members}
    return render_to_response("main/class/class_details.html", rc, context_instance=RequestContext(request))

def class_file_upload(request):
    rc={}
    return render_to_response("main/class/file_upload.html", rc, context_instance=RequestContext(request))

def add_class(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = Class.objects.filter(pk=pk)
    if c:
        UserClassData(user_info = request.user.user_info, class_obj = c[0]).save()
        if not Activity.objects.filter(target__target_type='Class', activity_type='joined', actor=request.user, target__target_id=c[0].pk).exists():
            Activity.create('joined',request.user,c[0])
        return {'status':'success'}
    return {'status': 'class does not exist'}

def drop_class(request,pk):
    if request.user.is_anonymous():
        return {'status': 'user not authenticated'}
    c = Class.objects.filter(pk=pk)
    if c:
        UserClassData.objects.filter(user_info = request.user.user_info, class_obj = c[0]).delete()
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
