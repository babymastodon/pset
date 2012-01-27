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

import re

def front_page(request):
    rc={}
    rc['rform'] = EmailRegisterForm() 
    return render_to_response("main/home/front_page.html", rc, context_instance=RequestContext(request))

@login_required
def home_page(request):
    rc={}
    user = request.user
    rc['user'] = user
    rc['user_info'] = user.user_info
    rc['classes'] = user.user_info.klasses
    rc['friends'] = user.user_info.friends
    defaults = {}
    defaults['user_info']=request.user.user_info
    defaults['class_obj']="" 
    defaults['instructor']=defaults['recitation_leader']=defaults['experience']=""
    form = AddClassForm(defaults)
    if request.method=="POST":
        form = AddClassForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            newclass = UserClassData()
            newclass.user_info = user.user_info
            newclass.instructor = d['instructor']
            newclass.recitation_leader = d['recitation_leader']
            newclass.experience = d['experience']
            klass = re.search("\w+\.\w+", d['class_obj'])
            klass_num = ClassNumber.objects.filter(number=klass.group())
            if klass_num:
                userinfo = UserInfo.objects.filter(user=request.user)
                if userinfo:
                    user_info_obj = userinfo[0]
                    newclass.user_info = user_info_obj
                    klass_obj = klass_num[0].class_obj
                    newclass.class_obj = klass_obj
                    newclass.save()
                    Activity.create(actor=request.user, activity_type="joined", target=klass_obj)
                else:
                    rc['error'] = "No userinfo found"
            else:
                rc['error'] = "Class Number is invalid"
        else:
            rc['error'] = form.errors
    # passing stuff to the home page
    rc['form'] = form
    return render_to_response("main/home/home_page.html", rc, context_instance=RequestContext(request))

def add_class(request):
    rc={error:None}
    if request.method=="POST":
        form = AddClassForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            newclass = UserClassData()
            newclass.user_info = request.user.user_info
            newclass.instructor = d['instructor']
            newclass.recitation_leader = d['recitation_leader']
            newclass.experience = d['experience']
            klass = re.search("\w+\.\w+", d['klass'])
            try:
                party.class_obj = ClassNumber.objects.get(number=klass.group()).class_obj
                status=None
            except Exception as e:
                rc['error'] = "Class Number is invalid"
                raise e
    retu
            

def about(request):
    rc={}
    return render_to_response("main/home/about.html", rc, context_instance=RequestContext(request))

