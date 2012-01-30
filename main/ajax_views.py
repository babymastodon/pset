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
import main.search_views as search_views
import main.party_views as party_views
import  main.class_views as class_views
import main.comment_views as comment_views
import main.people_views as people_views

def ajax(request):
    module = request.REQUEST.get("module","")
    if module=="search":
        return search_views.ajax(request)
    elif module=="party":
        return party_views.ajax(request)
    elif module=="class":
        return class_views.ajax(request)
    elif module=="comments":
        return comment_views.ajax(request)
    elif module=="people":
        return people_views.ajax(request)
    else:
        return HttpResponse('{"status":"module not found"}', mimetype="application/json");

