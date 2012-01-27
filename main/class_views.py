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

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def class_details(request, pk):
    rc={}
    rc['class'] = get_object_or_404(Class,pk=pk)
    rc['newsfeed'] = Activity.objects.filter(target__target_type='Class', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[:10]
    rc['comments']={'pk':pk, 'target':"Class"}
    return render_to_response("main/class/class_details.html", rc, context_instance=RequestContext(request))

def class_file_upload(request):
    rc={}
    return render_to_response("main/class/file_upload.html", rc, context_instance=RequestContext(request))

def ajax(request):
    pass
