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

def string_or_blank(s):
    if s:
        return str(s)
    return ""

def create_party_dict(ob, letter, request, color="red"):
    (lat,lng) = [(random.random()-.5)*.01+x for x in (42.35886, -71.09356)]
    r = {}
    r['title'] = ob.get_name()
    r['letter'] = letter
    r['day_name'] = ob.get_day_name()
    r['day'] = ob.get_day()
    r['start_time'] = ob.get_start_time()
    r['end_time'] = ob.get_end_time()
    r['agenda'] = "Agenda: " + ob.agenda
    r['location'] = ob.location
    r['room'] = "Room: " + ob.room
    r['detail_url'] = ob.get_link()
    r['bldg_img'] = ob.get_image()
    r['lat'] = ob.lat
    r['lng'] = ob.lng
    r['class_nums'] = [x.number for x in ob.class_obj.get_meta()]
    r['class_title'] = ob.class_obj.get_name() 
    r['color'] = color
    r['pk'] = ob.pk
    return r

def party_register_helper_func(party, user):
    UserPartyTable(user=user, party=party).save()
    party.save()
    if not Activity.objects.filter(target__target_type='Party', actor=user, target__target_id=party.pk, activity_type='attending').exists():
        Activity.create(actor=user, activity_type="attending", target=party)

def make_party_list(request, queryset, counter=0):
    #available colors are: blue brown darkgreen green orange paleblue pink purple red yellow
    colorlist = ['red','orange','yellow','green','blue','purple']
    letterlist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result_list=[]
    for i in queryset:
        r = create_party_dict(i, letterlist[counter%26], request, color=colorlist[(counter/26)%6])
        result_list.append(r)
        counter+=1
    return result_list

def get_parties_personalized(request):
    if request.user.is_authenticated():
        result_list = make_party_list(request, (a.party for a in personalized_party_query(request)))
        return {'status':'success', 'result_list':result_list}
    return {"status":"not authenticated"}

def personalized_party_query(request):
    now=timezone.now()
    return UserPartyTable.objects.filter(
            (
                Q(user__user_info__in=request.user.user_info.followees.all()) |
                Q(party__class_obj__in=request.user.user_info.klasses.all()) |
                Q(user__user_info=request.user.user_info)
            ) & (
                    Q(party__endtime__gt=now) &
                    Q(party__starttime__lt=now+timedelta(days=7)) &
                    Q(party__active=True)
            )
        ).order_by('party', 'party__starttime').distinct('party').select_related(depth=1)

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
   
def get_history(request, historytype, pk=9001, page=1, num=6):
    r={}
    r['show_all'] = reverse('main.party_views.all_history', kwargs={'historytype':historytype, 'pk':pk, 'page':page})
    r['extended']=False
    def slice_query(qs):
        return qs.filter(endtime__lt=timezone.now()).order_by('-starttime')[(page-1)*num: (page)*num]
    if historytype=='all':
        r['list'] = slice_query(Party.objects.all())
    elif historytype=='person':
        user = get_object_or_404(User, pk=pk)
        if (not user.user_info.private_profile) or request.user.is_authenticated():
            qs = user.user_info.user.party_set_attend.all()
            r['list'] = slice_query(qs)
        else:
            r['list']=[]
    elif historytype=='class':
        klass = get_object_or_404(Class, pk=pk)
        qs = klass.party_set.all()
        r['list'] = slice_query(qs)
    else:
        r['list']=[]
    return r

def get_newsfeed(request, feedtype, pk=9001, page=1):
    r={}
    r['link'] = reverse("main.common_views.all_newsfeed", kwargs={'feedtype':feedtype, 'page':1, 'pk':pk})
    r['header']="Recent Activity"
    qs = Activity.objects.all()
    def slice_query(num, qs):
        return qs.order_by('-time_created')[(page-1)*num: (page)*num]
    if request.user.is_anonymous():
        qs = qs.filter(actor__user_info__private_activities=False)
    if feedtype=="profile":
        qs = qs.filter(
                (Q(target__target_type='User') & Q(target__target_id=pk) & ~Q(activity_type='comment')) |
                (Q(actor__pk=pk))
                )
        r['feed'] = slice_query(6, qs)
        n = User
    if feedtype=='class':
        klass = get_object_or_404(Class, pk=pk)
        related_parties = klass.party_set.all()#lol, it pulled the correct ids for the IN query
        qs = qs.filter(
                (Q(target__target_type='Class') & Q(target__target_id=pk) & ~Q(activity_type='comment')) |
                (Q(target__target_type='Party') & Q(target__target_id__in=related_parties))
            )
        r['feed'] = slice_query(6, qs)
        n=Class
    if feedtype=='party':
        qs = qs.filter(
                (Q(target__target_type='Party') & Q(target__target_id=pk) & ~Q(activity_type='comment'))
            )
        r['feed'] = slice_query(6, qs)
        n=Party
    if feedtype=='personalized':
        ui = request.user.user_info
        qs = qs.filter(
                (Q(target__target_type='Party') & Q(target__target_id__in=ui.user.party_set_attend.all())) |
                (Q(actor__pk__in=ui.followees.all())) |
                (Q(target__target_type='User') & Q(target__target_id__in=ui.followees.all())) |
                (Q(target__target_type='Class') & Q(target__target_id__in=ui.klasses.all()))
            ).order_by("-time_created")
        r['feed'] = slice_query(15, qs)

    #get the name of the thingy
    try:
        r['name'] = n.objects.get(pk=pk).get_name()
    except Exception as e:
        pass
    return r

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
