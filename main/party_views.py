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
from people_views import *
from account_views import fetch_fullname

def party_details(request, pk):
    rc={}
    party = get_object_or_404(Party, pk=pk)
    rc['party'] = party
    rc['pk'] = pk
    attending=request.GET.get('attending',None)
    if attending and request.user.is_authenticated():
        party_register_helper_func(party, request.user)
    #list of all attendees
    attendees = get_all_attending(request, pk)
    numpeople=len(attendees)
    all_attendees_header = str(numpeople) + (" People " if numpeople!=1 else " Person ") + "Attending"
    rc['all_attendees'] = {"show_all":reverse("main.people_views.all_attending", kwargs={"pk":pk}), 'list':attendees[:10], 'header':all_attendees_header}
    #list of all admins
    admins = party.admins.all()
    rc['admins'] = {'list':admins, 'header':'Admins'}
    rc['isadmin'] = admins.filter(pk=request.user.pk).exists()
    #friend rank
    #newsfeed
    page = int(request.GET.get("page","1"))
    if request.user.is_authenticated():
        if not party.attendees.filter(pk=request.user.pk).exists():
            rc['not_registered'] = True
    rc['newsfeed'] = get_newsfeed(request,'party', pk)
    rc['comments']={'pk':pk, 'target':"Party"}
    return render_to_response("main/party/party_details.html", rc, context_instance=RequestContext(request))

@login_required
def invite_friends(request, pk):
    rc={}
    party = get_object_or_404(Party, pk=pk)
    rc['party'] = party
    if request.method=="POST":
        data = simplejson.loads(request.POST.get("people_data"))
        if data:
            pks = set()
            emails = set()
            for key in data:
                if data[key] == "email":
                    u = User.objects.filter(email=key)
                    if u:
                        pks.ad(u.pk)
                    else:
                        emails.add(key)
                else:
                    pks.add(key)
            rc['emails'] = []
            rc['invitees'] = []
            rc['already'] = []
            for key in pks:
                invitee = User.objects.filter(pk=key)
                if not party.attendees.filter(pk=key).exists():#if he is not already goign to the party
                    if invitee:
                        invitee = invitee[0]
                        rc['invitees'].append(invitee)
                        create_invite(request, sender=request.user, invitee=invitee, party=party)
                else:
                    rc['already'].append(invitee[0])
            for email in emails:
                if re.match(r'[^@]+@mit.edu', email):
                    username = email.split('@')[0]
                    first,last = fetch_fullname(username)
                    if first or last:
                        name = first + " " + last
                    else:
                        name = username
                    root_url = request.get_host()
                    rc['emails'].append(email + " - " + name)
                    email_rc = {}
                    ih = InviteHash.create(party, email)
                    email_rc['link'] = root_url +ih.get_invite_link()
                    email_rc['party'] = party
                    email_rc['sender'] = request.user
                    send_email(request, email,request.user.get_name() + " has invited you to a pset party!",'signup.html', email_rc)
            rc['invitees'] = sorted(rc['invitees'], key=lambda x: x.get_name())
            rc['emails'] = sorted(rc['emails'])
            rc['already'] = sorted(rc['already'], key=lambda x: x.get_name())
            return render(request, 'main/party/invitations_sent.html', rc)
        else:
            rc['error'] = "The server did not recieve the people list"

    return render(request, 'main/party/invite_friends_page.html', rc)


@login_required
def edit_party(request, pk):
    rc={'error':None}
    defaults = {}
    party = get_object_or_404(Party, pk=pk)
    if not party.admins.filter(pk=request.user.pk):
        raise Http404
    defaults['day'] = date_string(party.starttime)
    defaults['title'] = party.title
    defaults['agenda']= party.agenda
    defaults['klass']= string.join([x.number for x in party.class_obj.get_meta()], ', ')
    defaults['room']=party.room
    defaults['start_time'] = time_string(party.starttime)
    defaults['end_time'] = time_string(party.endtime)
    defaults['location'] = party.location
    defaults['lng'] = party.lng
    defaults['lat'] = party.lat
    defaults['building_img'] = party.building_img
    form = PartyCreateForm(defaults)
    if request.method=="POST":
        form = PartyCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
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
                party.save()
                Activity.create(actor=request.user, activity_type="edited", target=party)
                return redirect(party.get_link())
            else:
                rc['error'] = "Class Number is invalid"
        else:
            rc['error'] = "There were errors in the form. Please make sure that all the fields are filled out."
    rc['form'] = rc['rform'] =  form
    return render_to_response("main/party/edit_party.html", rc, context_instance=RequestContext(request))

def party_create(request):
    rc={'error':None}
    now = timezone.now()
    defaults = {}
    defaults['day'] = date_string(now)
    #set the default field values
    defaults['title']=defaults['agenda']=defaults['klass']=defaults['room']=""
    klass_pk = request.GET.get('class')
    if klass_pk:
        klass_qs = Class.objects.filter(pk=klass_pk)
        if klass_qs:
            defaults['klass'] = string.join([x.number for x in klass_qs[0].get_meta()],', ')
    defaults['start_time'] = time_string(now)
    defaults['end_time'] = time_string(now+timedelta(hours=1))
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
                    for user in party.class_obj.userinfo_set.all().exclude(pk=creator.pk):
                        if user.email_party:
                            email_rc={}
                            email_rc['party'] = party
                            email_rc['creator'] = creator
                            email_rc['recipient'] = user.user
                            email_rc['link'] = party.get_link() + "?attending=1"
                            send_email(request, user.user.email, creator.get_name() + " is hosting a pset party for your class", 'newparty.html', email_rc)
                    return redirect(next_url)
            else:
                rc['error'] = "Class Number is invalid"
        else:
            rc['error'] = "There were errors in the form. Please make sure that all the fields are filled out."
    rc['form'] = rc['rform'] =  form
    return render_to_response("main/party/party_create.html", rc, context_instance=RequestContext(request))


def all_history(request, historytype, pk, page):
    rc={}
    page=int(page)
    rc['history'] = get_history(request, historytype, pk, page, 20)
    rc['page'] = page
    rc['next'] = reverse('main.party_views.all_history', kwargs={'historytype':historytype, 'pk':pk, 'page':page+1})
    if page>1:
        rc['prev'] = reverse('main.party_views.all_history', kwargs={'historytype':historytype, 'pk':pk, 'page':page-1})
    if historytype=="class":
        klass = get_object_or_404(Class, pk=pk)
        rc['title'] = "Party history for " + klass.get_name()
        rc['back'] = klass.get_link()
    elif historytype=="person":
        person = get_object_or_404(User, pk=pk)
        rc['title'] = "Parties that " + Person.get_name() + " has attended"
        rc['back'] = person.get_link()
    else:
        rc['title'] = "All past pset parties"
        rc['back'] = reverse('main.search_views.parties_by_date')
    rc['history']['show_all']=False
    rc['history']['expanded']=True
    return render(request, 'main/party/all_history.html', rc)

@login_required
def party_cancel(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if not party.admins.filter(pk=request.user.pk).exists():
        return redirect(party.get_link())
    if request.method=="POST":
        party.active=False
        party.save()
        Activity.create(actor=request.user, activity_type="canceled", target=party)
        return redirect(party.get_link())
    return render(request, "main/party/party_cancel_ensure.html", {'party':party})

@login_required
def party_uncancel(request, pk):
    party = get_object_or_404(Party, pk=pk)
    if not party.admins.filter(pk=request.user.pk).exists():
        return redirect(party.get_link())
    party.active=True
    party.save()
    Activity.create(actor=request.user, activity_type="uncanceled", target=party)
    return redirect(party.get_link())

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
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

