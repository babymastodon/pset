from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date, timedelta
from django import forms
import account_views
from django.utils import timezone
import simplejson, string, re

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def party_details(request, pk):
    rc={}
    party = get_object_or_404(Party, pk=pk)
    rc['party'] = party
    #list of all attendees
    attendees = party.attendees.all()[:10]
    numpeople=len(attendees)
    all_attendees_header = str(numpeople) + (" People " if numpeople!=1 else " Person ") + "Attending"
    rc['all_attendees'] = {"show_all":reverse("main.people_views.all_attending", kwargs={"pk":pk}), 'list':attendees, 'header':all_attendees_header}
    #list of all admins
    admins = party.admins.all()
    rc['admins'] = {'list':admins, 'header':'Admins'}
    #friend rank
    #newsfeed
    page = int(request.GET.get("page","1"))
    attending=request.GET.get('attending',None)
    if attending and request.user.is_authenticated():
        party_register_helper_func(party, request.user)
    rc['newsfeed'] = get_newsfeed(request,'party', pk)
    rc['comments']={'pk':pk, 'target':"Party"}
    return render_to_response("main/party/party_details.html", rc, context_instance=RequestContext(request))

def party_create(request):
    rc={'error':None}
    now = timezone.localtime(timezone.now())
    defaults = {}
    defaults['day'] = now.strftime("%m/%d/%y")
    def clean_time(s):
        return s.lower().lstrip('0')
    #set the default field values
    defaults['title']=defaults['agenda']=defaults['klass']=defaults['room']=""
    klass_pk = request.GET.get('class')
    if klass_pk:
        klass_qs = Class.objects.filter(pk=klass_pk)
        if klass_qs:
            defaults['klass'] = string.join([x.number for x in klass_qs[0].get_meta()],', ')
    defaults['start_time'] = clean_time(now.strftime("%I:%M%p"))
    defaults['end_time'] = clean_time((now+timedelta(hours=1)).strftime("%I:%M%p"))
    defaults['location'] = "W20: Stratton Student Center"
    defaults['lng'] = "-71.094774920000006"
    defaults['lat'] = "42.359042619999997"
    defaults['building_img'] = "http://web.mit.edu/campus-map/objimgs/object-W20.jpg"
    form = PartyCreateForm(defaults)
    if request.method=="POST":
        form = PartyCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            party = Party()
            party.starttime = datetime.combine(d['day'],d['start_time'])
            endday = d['day'] if d['start_time'] < d['end_time'] else d['day'] + timedelta(days=1)
            party.endtime = datetime.combine(endday, d['end_time'])
            party.title = d['title']
            party.agenda = d['agenda']
            party.location = d['location']
            party.room = d['room']
            party.lat = d['lat']
            party.lng = d['lng']
            party.building_img = d['building_img']
            klass = re.search("\w+\.\w+", d['klass'])
            klass_num = ClassNumber.objects.filter(number=klass.group().upper())
            if klass_num:
                klass_obj = klass_num[0].class_obj
                party.class_obj = klass_obj
                status=None
                if request.user.is_anonymous():
                    if d['username']:
                        user = authenticate(username = d['username'], password = d['password'])
                        if user:
                            login(request, user)
                            status="logged_in"
                        else:
                            rc['error']="Username and Password are not valid"
                    elif d['email']:
                        if d['pw1']==d['pw2'] and d['pw1']:
                            moo = account_views.create_from_email_pwd(email=d['email'], pwd=d['pw1'], request=request)
                            rc.update(moo['rc'])
                            if not rc.get('error'):
                                status="account_created"
                        else:
                            rc['error']="Passwords don't match"
                else:
                    status="logged_in"
                if status=="logged_in":
                    party.active=True
                    party.save()
                    creator=request.user
                    next_url = reverse('main.party_views.party_details', kwargs={'pk':party.pk})
                elif status=="account_created":
                    party.active=False
                    party.save()
                    creator=moo['user']
                    moo['ph'].party=party
                    moo['ph'].save()
                    next_url = reverse('main.account_views.email_sent')
                if status:
                    party.attendees.add(creator)
                    party.admins.add(creator)
                    party.save()
                    Activity.create(actor=creator, activity_type="created", target=party)
                    Activity.create(actor=creator, activity_type="attending", target=party)
                    return redirect(next_url)
            else:
                rc['error'] = "Class Number is invalid"
        else:
            rc['error'] = "There were errors in the form. Please make sure that all the fields are filled out."
    rc['form'] = rc['rform'] =  form
    return render_to_response("main/party/party_create.html", rc, context_instance=RequestContext(request))

def party_registered(request, pk):
    rc={}
    p = get_object_or_404(Party, pk=pk)
    rc['event_name']=p.get_name()
    rc['event_location']=p.location
    rc['event_time']=p.get_day() + " at " + p.get_start_time()
    rc['title']="Let the games begin!"
    rc['pk']=pk
    return render_to_response("main/party/party_registered.html", rc, context_instance=RequestContext(request))

def party_unregistered(request, pk):
    rc={}
    p = get_object_or_404(Party, pk=pk)
    rc['event_name']=p.get_name()
    rc['event_location']=p.location
    rc['event_time']=p.get_day() + " at " + p.get_start_time()
    rc['title']="Party Pooper :("
    rc['pk']=pk
    return render_to_response("main/party/party_unregistered.html", rc, context_instance=RequestContext(request))

def party_must_login(request, pk):
    rc={}
    rc['pk']=pk
    return render_to_response("main/party/party_login.html", rc, context_instance=RequestContext(request))

def party_register_helper_func(party, user):
    party.attendees.add(user)
    party.save()
    if not Activity.objects.filter(target__target_type='Party', actor=user, target__target_id=party.pk, activity_type='attending').exists():
        Activity.create(actor=user, activity_type="attending", target=party)

def party_register_ajax(request, party_pk):
    r = {}
    r["status"]="success"
    r['registered']=True
    r['authenticated']=True
    r['link'] = reverse('main.party_views.party_registered',kwargs={'pk':party_pk})
    if request.user.is_anonymous():
        r['link'] = reverse('main.party_views.party_must_login', kwargs={'pk':party_pk})
        r['authenticated']=False
        return r
    party = Party.objects.filter(pk=party_pk)
    if party:
        party_register_helper_func(party[0], request.user)
    else:
        r['status']='party does not exist'
    return r

def party_unregister_ajax(request, party_pk):
    r = {}
    r["status"]="success"
    r['registered']=False
    r['authenticated']=True
    r['link'] = reverse('main.party_views.party_unregistered',kwargs={'pk':party_pk})
    party = Party.objects.filter(pk=party_pk)
    if party and request.user.is_authenticated():
        party[0].attendees.remove(request.user)
    else:
        r['status']='party does not exist'
    return r

def is_registered(request, party_pk):
    party = Party.objects.filter(pk=party_pk)
    if party:
        if request.user.is_authenticated():
            if party[0].attendees.filter(pk=request.user.pk).exists():
                return {'status':'success', 'attending':True}
        return {'status':'success', 'attending':False}
    return {'status': 'party does not exist'}

#ajax handler for handling party update information and party delete
def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        party_pk = request.REQUEST.get('pk',None)
        if party_pk:
            party_pk=int(party_pk)
        if verb=='isregistered':
            result = is_registered(request, party_pk)
        elif verb=='get_attend_button':
            return render_to_response('main/party/attend_button.html',{'pk':party_pk})
        elif verb=='register':
            result=party_register_ajax(request, party_pk)
        elif verb=='unregister':
            result=party_unregister_ajax(request, party_pk)
        elif verb=='all_attendees':
            return all_attendees(request, party_pk)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

