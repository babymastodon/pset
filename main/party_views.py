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

def party_details(request):
    rc={}
    return render_to_response("main/party/party_details.html", rc, context_instance=RequestContext(request))

def party_create(request):
    rc={}
    return render_to_response("main/party/party_create.html", rc, context_instance=RequestContext(request))

#ajax handler for handling party update information and party delete
def ajax(request):
    pass

