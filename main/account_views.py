from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as django_login
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, date
from django.db import IntegrityError
from django.template import loader, Context
from django import forms
from django.utils import timezone
import random
import urllib
import re
from itertools import chain

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *
from main.people_views import *
from BeautifulSoup import BeautifulSoup

def login(request, user):
    request.session['last_authenticate']=timezone.now()
    request.session.modified = True
    django_login(request,user)

def fetch_fullname(username):
    # Returns tuple: [firstName, lastName]
    params = urllib.urlencode({'query':username})
    htmldoc = urllib.urlopen("http://web.mit.edu/bin/cgicso?options=general&" + params)
    soup = BeautifulSoup(htmldoc.read())
    data = soup.find('pre') or [1] # put in array with one element in case connection failed
    #data='   name: Drach, Zachary email: <a href="mailto:zdrach@MIT.EDU">zdrach@MIT.EDU</a> address: MacGregor House # F413 year: 1 '
    if len(data) <= 1:
        return ("","")
    else:
        m = re.search("(?<=name: )(\w+), (\w+)", data.contents[0])
        if m == None:
            return ("","") 
        name = (str(m.group(2)), str(m.group(1)))  # [firstName, lastName]
        return name

#Helper functions
#function for creating and saving account
def createAccount(email="", username="", first_name="", last_name="", 
                  password="", is_active=True):
    user = User.objects.create_user(username.lower(), email=email.lower(), password=password)
    user.is_active = is_active
    if not first_name and not last_name:
        (first_name, last_name) = fetch_fullname(username)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    userdata = UserInfo()
    userdata.user = user
    userdata.save()
    
    return user

#views start here
def profile_page(request, pk):
    rc={}
    user = get_object_or_404(User, pk=pk)
    rc['person']=user
    if (not user.user_info.private_profile) or request.user.is_authenticated():
        rc['private']=False
        rc['newsfeed'] = get_newsfeed(request,'profile',pk)
        rc['comments']={'pk':pk, 'target':"User"}
        rc['join_date']=day_string(user.date_joined)
        rc['classes'] = user.user_info.klasses.all()
        rc['last_seen']=time_ago(user.user_info.last_seen)
        rc['followees'] = {"show_all":reverse("main.people_views.all_followees", kwargs={"pk":pk}), 'header':"Is Following", "list":get_followees(request, pk)[0:5]}
        rc['followers'] = {"show_all":reverse("main.people_views.all_followers", kwargs={"pk":pk}), 'header':"Is Being Followed By", "list":get_followers(request, pk)[0:5]}
        rc['following'] = get_followers(request,pk).filter(pk=request.user.user_info.pk).exists()
        rc['history'] = get_history(request, 'person', pk)
        rc['history']['header'] = "Parties Attended"
    else:
        rc['private'] = True
    return render_to_response("main/account/profile_page.html", rc, context_instance=RequestContext(request))

@login_required
def manage_classes(request):
    pass

@login_required
def my_profile_page(request):
    return profile_page(request, request.user.pk)

@login_required
def profile_new_user_info(request):
    rc={}
    return render_to_response("main/account/profile_new_user_info.html", rc, context_instance=RequestContext(request))

def create_from_email_pwd(email, pwd, request):
    rc={}
    user=ph=None
    uname=email.split("@")[0]
    account = User.objects.filter(username=uname)
    if account:
        account = account[0]
        if account.is_active:
            rc['error']='You already have an account. Did you <a href="' + reverse("main.account_views.forgot_password") + '" class="underlined">forget your password?</a>'
            return {'rc':rc}
    else:
        account=createAccount(email=email, username=uname, password=pwd, is_active=False)
    ph = PendingHash.create(user=account)
    ph.save()
    root_email = request.get_host()
    send_email(request, email, 'InTheLooop Email Verification', 'verify.html', {
        'person':account,
        'link':root_email+reverse('main.account_views.verify', kwargs={'hashcode':ph.hashcode}),
    })
    rc['email'] = email
    return {'rc':rc, 'user':account, 'ph':ph}
    

def create_account_page(request):
    rc={}
    form = EmailRegisterForm()
    if request.method=="POST":
        form = EmailRegisterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['pw1']==form.cleaned_data['pw2'] and form.cleaned_data['pw1']:
                email=form.cleaned_data['email']
                boo = create_from_email_pwd(email=email, pwd=form.cleaned_data['pw1'], request=request)
                rc.update(boo['rc'])
                if not rc.get('error'):
                    return redirect('main.account_views.email_sent')
            else:
                rc['error']="Passwords don't match"
    rc['rform'] = form
    return render_to_response("main/account/create_account_page.html", rc, context_instance=RequestContext(request))

def reset_email_sent(request):
    return render(request, 'main/account/reset_email_sent.html')

def forgot_password(request):
    rc={}
    form = EmailForm()
    if request.method=="POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email.lower())
            if user:
                user = user[0]
                ph = PendingHash.create(user)
                ph.save()
                root_email = request.get_host()
                send_email(request, email, "Reset Password", 'forgot.html', {
                    'person':user,
                    'link': root_email+reverse('main.account_views.reset_password_hashcode', kwargs={'hashcode':ph.hashcode})
                })
                return redirect(reverse('main.account_views.reset_email_sent'))
            else:
                rc['error'] = "You do not have an account yet"
        else:
            rc['error']="Email address was invalid"
    rc['form'] = form
    return render_to_response("main/account/forgot_password.html", rc, context_instance=RequestContext(request))

def reset_password_hashcode(request, hashcode):
    rc={}
    user = authenticate(hashcode=hashcode)
    if not user:
        return render_to_response("main/account/password_expired.html", rc, context_instance=RequestContext(request))
    login(request,user)
    return redirect(reverse('main.account_views.change_password'))

def re_auth(request):
    rc={}
    form = PasswordForm()
    if request.method=="POST":
        form = PasswordForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            user = authenticate(username = request.user.username, password=d['password'])
            if user:
                login(request,user)
                request.session['last_authenticate'] = timezone.now()
                return render(request, 'main/account/change_password.html', {'form':ResetPasswordForm()})
        rc['error'] = "Password is invalid"
    rc['form'] = form
    return render(request, 'main/account/re_auth.html', rc)

@login_required
def change_password(request):
    rc={}
    if (not 'last_authenticate' in request.session) or  timezone.now() - request.session['last_authenticate'] > timedelta(minutes=2):
        return re_auth(request)
    form = ResetPasswordForm()
    if request.method=="POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            if d['pw1']==d['pw2'] and d['pw1']:
                request.user.set_password(d['pw1'])
                request.user.save()
                return redirect(reverse('main.account_views.account_info'))
        rc['error'] = "Passwords don't match"
    rc['form'] = form
    return render(request, 'main/account/change_password.html', rc)

def set_password_expired(request, pk):
    n = reverse('main.party_views.party_details', kwargs={'pk':pk})+"?attending=1"
    link = reverse('main.account_views.login_page')+"?next=" + urllib.quote(n)
    return render(request, 'main/account/set_password_expired.html', {'link':link})

def invite_hashcode(request, hashcode, pk):
    rc={}
    ihs = InviteHash.objects.filter(hashcode=hashcode)
    if not ihs:
        if request.user.is_authenticated():
            return redirect( reverse('main.party_views.party_details', kwargs={'pk':pk})+"?attending=1")
        return set_password_expired(request, pk)
    ih = ihs[0]
    uname = ih.email.split("@")[0]
    if User.objects.filter(username=uname).exists():
        ihs.delete()
        return set_password_expired(request, pk)
    form = ResetPasswordForm()
    if request.method=="POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            if d['pw1']==d['pw2'] and d['pw1']:
                u = createAccount(username=uname, password=d['pw1'], email=ih.email)
                u = authenticate(username=uname, password=d['pw1'])
                login(request, u)
                party_register_helper_func(ih.party, u)
                ihs.delete()
                return redirect(reverse('main.account_views.bio_info'))
        rc['error']="Passwords don't match"
    rc['form'] = form
    rc['username']=uname
    return render(request, 'main/account/set_password.html', rc)
        

def email_sent(request):
    rc={}
    return render_to_response("main/account/create_from_email_sent.html", rc, context_instance=RequestContext(request))

def verify(request, hashcode):
    rc={}
    user = authenticate(hashcode=hashcode)
    if not user:
        return render_to_response("main/account/verify_expired.html", 
                                  rc, context_instance=RequestContext(request))
    Activity.create(actor=user, activity_type='newaccount')
    login(request,user)
    return redirect(reverse('main.account_views.bio_info'))

def link_to_facebook(request):
    rc={}
    return render_to_response("main/account/link_to_facebook.html", rc, context_instance=RequestContext(request))

@login_required
def account_info(request):
    rc={}
    ui = request.user.user_info
    defaults={'email_invitations': ui.email_invitations, 'email_comment': ui.email_comment, 'email_party': ui.email_party, 'private_profile': ui.private_profile, 'private_activities': ui.private_activities, 'private_comments': ui.private_comments}
    form = AccountSettingsForm(defaults)
    if request.method=="POST":
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            ui.email_invitations = d['email_invitations']
            ui.email_comment = d['email_comment']
            ui.email_party = d['email_party']
            ui.private_profile = d['private_profile']
            ui.private_activities = d['private_activities']
            ui.private_comments = d['private_comments']
            ui.save()
            return redirect(reverse('main.account_views.my_profile_page'))
        else:
            rc['error'] = "There were errors in the form"
    rc['email_settings'] = [form['email_invitations'], form['email_party'], form['email_comment']]
    rc['privacy_settings'] = [form['private_profile'], form['private_activities'], form['private_comments']]
    return render_to_response("main/account/account_info.html", rc, context_instance=RequestContext(request))

def new_bio_info(request):
    return bio_info(request, True)

@login_required
def bio_info(request, new=False):
    rc={}
    defaults={}
    defaults['first_name'] = request.user.first_name
    defaults['last_name'] = request.user.last_name
    defaults['department'] = request.user.user_info.department
    defaults['graduation_year'] = string_or_blank(request.user.user_info.graduation_year)
    defaults['bio'] = request.user.user_info.bio
    form = UserBioForm(defaults)
    rc['department_choices']=str(department_choices)
    if new:
        rc['title'] = "Tell us a bit about yourself before getting started"
    else: 
        rc['title'] = "Edit your profile information"
    if request.method=="POST":
        form = UserBioForm(request.POST, request.FILES)
        if form.is_valid():
            i = request.user.user_info
            d = form.cleaned_data
            request.user.first_name = d['first_name']
            request.user.last_name = d['last_name']
            i.department = d['department']
            try:
                if d['graduation_year']:
                    if (len(d['graduation_year'])!=4):
                        raise ValueError("Year is not the right length")
                    year = int(d['graduation_year'])
                    i.graduation_year = year
            except ValueError:
                rc['error']="Please enter a valid year"
            i.bio = d['bio']
            ##process picture
            try:
                if d['pic']:
                    image = resize_image(d['pic'], 300)
                    i.image.save(d['pic'].name+"-"+str(timezone.localtime(timezone.now())), image)
            except Exception as e:
                raise e
                rc['error'] = "Image file could not be processed"
            if not 'error' in rc:
                i.reindex=True
                i.save()
                request.user.save()
                return redirect('main.account_views.my_profile_page')
        else:
            #most likely an invalid department
            rc['error']="Please enter a valid department name"
    rc['form']=form
    return render(request, 'main/account/bio_info.html', rc)
    
def login_page(request):
    rc={}
    n = request.GET.get('next',reverse('main.home_views.home_page'))
    if request.user.is_authenticated():
        return HttpResponseRedirect(n)
    form = LoginForm()
    if request.method=="POST":
        form = LoginForm(request.POST)
        n = request.POST['next']
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], 
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(n)
        rc['error']="Username and Password were invalid"
    if n:
        rc['next']=n
    rc['form']=form
    rc['rform']=EmailRegisterForm()
    return render_to_response("main/account/login_page.html", rc, 
                              context_instance=RequestContext(request))

def login_facebook(request):
    rc={}
    return render_to_response("main/account/login_facebook.html", rc, 
                              context_instance=RequestContext(request))

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect("main.home_views.front_page")

