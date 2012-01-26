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
    t = loader.get_template('main/party/comment_item.html')
    c = RequestContext(request, {
        'comments':comments,
    })
    return t.render(c)

def load_comments(request, target, pk, page):
    comments = Comment.objects.filter(target__target_type=target, target__target_id=pk).order_by('-time_created')[(page-1)*6:page*6]
    return {'status':'success', 'html':render_comments(request,comments)}


def post_comment(request, comment, target, pk):
    if request.user.is_authenticated():
        t = target_dict.get(target)
        if target:
            tt = t.objects.filter(pk=pk)
            if tt:
                comment = Comment.create(comment, request.user, tt[0])
                return {'status': 'success', 'html':render_comments(request, [comment])}
            else:
                return {'status': "pk does not exist found"}
        else:
            return {'status':'bad target'}
    else:
        return {'status':"user is not authenticated", }

def get_comment_box(request):
    return render(request,"main/party/post_comment.html")

#ajax handler for handling party update information and party delete
def ajax(request):
    result={'status':"none"}
    try:
        verb = request.REQUEST.get('verb',None)
        target = request.REQUEST.get('target',None)
        page = request.REQUEST.get('page',None)
        pk = request.REQUEST.get('pk',None)
        if pk:
            pk=int(pk)
        if page:
            page=int(page)
        if verb=='load':
            result = load_comments(request, target, pk, page)
        elif verb=='post':
            comment = request.POST.get('comment', None)
            result = post_comment(request, comment, target, pk)
        elif verb=='get_box':
            return get_comment_box(request)
        else:
            result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")

