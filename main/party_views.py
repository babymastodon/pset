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
import simplejson, string, re

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def party_details(request, pk):
    rc={}
    party = get_object_or_404(Party, pk=pk)
    rc['party'] = party
    rc['admins'] = party.admins.all()
    rc['attendees'] = party.attendees.all()[:10]
    #friend rank
    #newsfeed
    page = int(request.GET.get("page","1"))
    rc['newsfeed'] = Activity.objects.filter(target__target_type='Party', target__target_id=pk).order_by('-time_created')[(page-1)*30:page*30]
    rc['comments']={'pk':pk, 'target':"Party"}
    return render_to_response("main/party/party_details.html", rc, context_instance=RequestContext(request))

def party_create(request):
    rc={'error':None}
    now = datetime.datetime.now()
    defaults = {}
    defaults['day'] = now.strftime("%m/%d/%y")
    def clean_time(s):
        return s.lower().lstrip('0')
    defaults['start_time'] = clean_time(now.strftime("%I:%M%p"))
    defaults['end_time'] = clean_time((now+timedelta(hours=1)).strftime("%I:%M%p"))
    defaults['location'] = "W20: Stratton Student Center"
    defaults['lng'] = "-71.094774920000006"
    defaults['lat'] = "42.359042619999997"
    defaults['building_img'] = "http://web.mit.edu/campus-map/objimgs/object-W20.jpg"
    defaults['title']=defaults['agenda']=defaults['klass']=defaults['room']=""
    form = PartyCreateForm(defaults)
    if request.method=="POST":
        form = PartyCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            party = Party()
            party.starttime = d['start_time']
            party.endtime = d['end_time']
            party.day = d['day']
            party.title = d['title']
            party.agenda = d['agenda']
            party.location = d['location']
            party.room = d['room']
            party.lat = d['lat']
            party.lng = d['lng']
            party.building_img = d['building_img']
            klass = re.search("\w+\.\w+", d['klass'])
            try:
                party.class_obj = ClassNumber.objects.get(number=klass.group()).class_obj
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
                    creator=request.user
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
            except Exception as e:
                rc['error'] = "Class Number is invalid"
                raise e
        else:
            rc['error'] = "There were errors in the form. Please make sure that all the fields are filled out."
    rc['form'] = rc['rform'] =  form
    return render_to_response("main/party/party_create.html", rc, context_instance=RequestContext(request))

def party_registered(request, pk):
    rc={}
    rc['event_name']='MOOMOMOO'
    rc['event_location']="Building 35"
    rc['event_time']="Monday, December 25 at 11:30pm"
    rc['title']="Let the games begin!"
    rc['pk']=pk
    return render_to_response("main/party/party_registered.html", rc, context_instance=RequestContext(request))

def party_unregistered(request, pk):
    rc={}
    rc['event_name']='MOOMOMOO'
    rc['event_location']="Building 35"
    rc['event_time']="Monday, December 25 at 11:30pm"
    rc['title']="Party Pooper :("
    rc['pk']=pk
    return render_to_response("main/party/party_unregistered.html", rc, context_instance=RequestContext(request))

def party_must_login(request, pk):
    rc={}
    rc['pk']=pk
    return render_to_response("main/party/party_login.html", rc, context_instance=RequestContext(request))

def party_register_ajax(request, party_pk):
    r = {}
    r["status"]="success"
    r['registered']=True
    r['link'] = reverse('main.party_views.party_registered',kwargs={'pk':party_pk})
    party = Party.objects.filter(pk=party_pk)
    if party and request.user.is_authenticated():
        party[0].attendees.add(request.user)
        party[0].save()
        if not Activity.objects.filter(target__target_type='Party', actor=request.user, target__target_id=party_pk).exists():
            Activity.create(actor=request.user, activity_type="attending", target=party[0])
    else:
        r['status']='party does not exist'
    return r

def party_unregister_ajax(request, party_pk):
    r = {}
    r["status"]="success"
    r['registered']=False
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
        if party[0].attendees.filter(pk=request.user.pk).exists():
            return {'status':'success', 'attending':True}
        else:
            return {'status':'success', 'attending':False}
    return {'status': 'party does not exist'}

#ajax handler for handling party update information and party delete
def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        party_pk = request.REQUEST.get('pk',None)
        if verb=='isregistered':
            result = is_registered(request, party_pk)
        elif verb=='get_attend_button':
            return render_to_response('main/party/attend_button.html',{'pk':party_pk})
        elif verb=='register':
            result=party_register_ajax(request, party_pk)
        elif verb=='unregister':
            result=party_unregister_ajax(request, party_pk)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

