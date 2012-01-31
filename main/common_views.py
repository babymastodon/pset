from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date
from django.template import loader, Context
from django.utils import timezone
from django.db.models import Q
import urllib
from django import forms
from itertools import chain

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *
def all_newsfeed(request, feedtype, pk, page=1):
    rc={}
    page = int(page)
    rc['feed'] = get_newsfeed(request, feedtype, pk, page)
    rc['next'] = reverse('main.common_views.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page+1})
    if page>1:
        rc['prev'] = reverse('main.common_views.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page-1})
    rc['page'] = page
    rc['feed']['link'] = None
    if feedtype=="profile":
        rc['back'] = get_object_or_404(User, pk=pk).get_link()
    elif feedtype=="class":
        rc['back'] = get_object_or_404(Class, pk=pk).get_link()
    if feedtype=="party":
        rc['back'] = get_object_or_404(Party, pk=pk).get_link()
    return render(request, 'main/modules/all_newsfeed.html', rc)
def social_buttons(request):
    return render(request, 'main/modules/social_buttons.html')
