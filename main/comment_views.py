from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.template import loader, Context
from django.conf import settings
from datetime import datetime, date
from django import forms
import simplejson

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

def render_comments(request, comments):
    t = loader.get_template('main/modules/comment_item.html')
    c = RequestContext(request, {
        'comments': [{'item':x, 'can_delete':x.can_delete(request.user)} for x in comments]
    })
    return t.render(c)

def load_comments(request, target, pk, last_id=None):
    comments = Comment.objects.filter(target__target_type=target, target__target_id=pk).order_by('-time_created')
    if last_id:
        comments = comments.filter(pk__lt=last_id)
    if request.user.is_anonymous():
        comments = comments.filter(actor__user_info__private_comments=False)
    comments = list(comments[:6])
    return {'status':'success', 'html':render_comments(request,comments), 'last_id': comments[-1].pk if comments else last_id}


def post_comment(request, comment, target, pk):
    if request.user.is_authenticated():
        t = target_dict.get(target)
        if target:
            tt = t.objects.filter(pk=pk)
            if tt:#tt is the target (party, class, or user)
                comment = Comment.create(comment, request.user, tt[0])
                if comment.target.target_type == "User":
                    us = User.objects.filter(pk=comment.target.target_id)
                    if us:
                        u = us[0]
                        if u.user_info.email_comment:
                            email_rc = {}
                            email_rc['comment'] = comment
                            email_rc['target'] = u
                            send_email(request, u.email, "InTheLoop: " +  comment.actor.get_name() + " commented on your profile", "comment.html", email_rc)
                return {'status': 'success', 'html':render_comments(request, [comment])}
            else:
                return {'status': "pk does not exist found"}
        else:
            return {'status':'bad target'}
    else:
        return {'status':"user is not authenticated", }

def get_box(request, template):
    return render(request,template)

def delete_comment(request, pk):
    c = Comment.objects.filter(pk=pk)
    if c:
        if c[0].can_delete(request.user):
            c[0].delete()
            return {'status':'success'}
        return {'status':"no permissions to delete"}
    return {'status':"object does not exist"}

#ajax handler for handling party update information and party delete
def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        target = request.REQUEST.get('target',None)
        pk = request.REQUEST.get('pk',None)
        if pk:
            pk=int(pk)
        if verb=='load':
            last_id=request.REQUEST.get('last_id')
            if last_id:
                last_id=int(last_id)
            result = load_comments(request, target, pk, last_id)
        elif verb=='post':
            comment = request.POST.get('comment', None)
            result = post_comment(request, comment, target, pk)
        elif verb=='get_box':
            return get_box(request,"main/modules/post_comment.html")
        elif verb=='ensure_delete':
            return get_box(request,"main/modules/ensure_delete.html")
        elif verb=='delete':
            result = delete_comment(request, pk)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

