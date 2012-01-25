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
import urllib
from django import forms

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
