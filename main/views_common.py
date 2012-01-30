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
import urllib
from django import forms
from itertools import chain

#import models and forms here
from main.models import *
from main.forms import *

def string_or_blank(s):
    if s:
        return str(s)
    return ""

def party_register_helper_func(party, user):
    party.attendees.add(user)
    party.save()
    if not Activity.objects.filter(target__target_type='Party', actor=user, target__target_id=party.pk, activity_type='attending').exists():
        Activity.create(actor=user, activity_type="attending", target=party)

#replacing the default login_required with our own
def login_required(f):
    def login_required_func(request, *args, **kwargs):
        if request.user.is_authenticated():
            #for debugging purposes only: automatically generate userinfos so no error
            if not UserInfo.objects.filter(user=request.user).exists():
                UserInfo(user=request.user).save()
            else:
                ui = request.user.user_info
                ui.last_seen = timezone.now()
                ui.save()
            return f(request, *args,**kwargs)
        return HttpResponseRedirect(reverse('main.account_views.login_page')+"?next="+urllib.quote(request.get_full_path()))
    return login_required_func
   
def all_newsfeed(request, feedtype, pk, page=1):
    rc={}
    page = int(page)
    rc['feed'] = get_newsfeed(request, feedtype, pk, page)
    rc['next'] = reverse('main.views_common.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page+1})
    if page>1:
        rc['prev'] = reverse('main.views_common.all_newsfeed', kwargs={'feedtype':feedtype, 'pk':pk, 'page':page-1})
    rc['page'] = page
    rc['feed']['link'] = None
    return render(request, 'main/modules/all_newsfeed.html', rc)

def get_newsfeed(request, feedtype, pk, page=1):
    r={}
    r['link'] = reverse("main.views_common.all_newsfeed", kwargs={'feedtype':feedtype, 'page':1, 'pk':pk})
    r['header']="Recent Activity"
    NUM_PER_PAGE=6
    qs = Activity.objects.all()
    if request.user.is_anonymous():
        qs = qs.filter(actor__user_info__private_activities=False)
    if feedtype=="profile":
        newsfeed1 = qs.filter(target__target_type='User', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[:page*NUM_PER_PAGE]

        newsfeed2 = qs.filter(actor__pk=pk).order_by('-time_created')[:page*NUM_PER_PAGE]
        smax = page*NUM_PER_PAGE-1
        smin = (page-1)*NUM_PER_PAGE-1
        if smin==-1:
            smin=None
        r['feed'] = sorted(chain(newsfeed1,newsfeed2),key=lambda x: x.time_created)[smax:smin:-1]
        n = User
    if feedtype=='class':
        r['feed'] = qs.filter(target__target_type='Class', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[(page-1)*NUM_PER_PAGE:page*NUM_PER_PAGE]
        n=Class
    if feedtype=='party':
        r['feed'] = qs.filter(target__target_type='Party', target__target_id=pk).exclude(activity_type='comment').order_by('-time_created')[(page-1)*NUM_PER_PAGE:page*NUM_PER_PAGE]
        n=Party
    #get the name of the thingy
    try:
        r['name'] = n.objects.get(pk=pk).get_name()
    except Exception as e:
        pass
    return r

def social_buttons(request):
    return render(request, 'main/modules/social_buttons.html')

def send_email(request, to, subject, template, rc):
    html = loader.get_template('emails/'+template)
    rc['root_url'] = request.get_host()
    c = RequestContext(request, rc)
    from_email = 'InTheLoop@'+request.get_host()
    msg = EmailMultiAlternatives(subject, html.render(c), from_email, [to])
    msg.content_subtype = "html"
    msg.send()

def create_invite(request, sender, invitee, party):
    root_url = request.get_host()
    i = Invitation(sender=sender, invitee=invitee, party=party)
    if invitee.user_info.email_invitations:
        email_rc={}
        email_rc['link'] = root_url + party.get_link() + "?attending=1" 
        email_rc['party'] = party
        email_rc['sender'] = request.user
        send_email(request, invitee.email, request.user.get_name() + " has invited you to a pset party!", 'invitation.html', email_rc)
    i.save()

"""
def send_invite(request):
    rc={}
    if request.user.first_name and request.user.last_name:
        rc['name'] = request.user.first_name + " " + request.user.last_name
    elif request.user:
        rc['name'] = request.user.username
    else:
        rc['name'] = "Dr. Incognito"
    rc['link'] = request.get_host()+reverse('main.party_views.party_details', kwargs={'pk':1})
    rc['event'] = "My Party"
    send_email(request, 'maxtang@mit.edu','Invite Email','signup.html', rc)
    return render_to_response("emails/signup.html", rc, context_instance=RequestContext(request))
"""
