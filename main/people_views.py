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

def all_attending(request, pk):
    rc={}
    rc['attendees'] = get_all_attending(request, pk)
    rc['title']= 'All Attending'
    return render_to_response("main/modules/people_popup.html", rc, context_instance=RequestContext(request))

def get_all_attending(request, pk):
    party = get_object_or_404(Party, pk=pk)
    attendees = party.attendees.all()
    return attendees
