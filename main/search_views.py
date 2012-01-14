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

def parties_by_class(request, pk):
    rc={}
    return render_to_response("main/search/parties_by_class.html", rc, context_instance=RequestContext(request))

def parties_by_date(request):
    rc={}
    return render_to_response("main/search/parties_by_date.html", rc, context_instance=RequestContext(request))

def search_page(request):
    rc={}
    return render_to_response("main/search/search_page.html", rc, context_instance=RequestContext(request))

def ajax_s(request):
    pass
