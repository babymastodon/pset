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
from haystack.query import SearchQuerySet
import logging, simplejson, string
from django.core import serializers

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

RESULTS_PER_PAGE = getattr(settings,'RESULTS_PER_PAGE',10)
logger = logging.getLogger(__name__)

def parties_by_class(request, pk):
    rc={}
    return render_to_response("main/search/parties_by_class.html", rc, context_instance=RequestContext(request))

def parties_by_date(request):
    rc={}
    return render_to_response("main/search/parties_by_date.html", rc, context_instance=RequestContext(request))

#takes a search query and an optional category. If no category, it tries to intelligently guess the
#cagetory. If the search query contains a class number, the search will try to make that result first
#it returns a dict with name, description, (picture), and related classes if a class. If a person,
#returns dict with name, class, department, (picture)
#format: {'page':int, 'numpages':int, 'results':[{'title':string,'description':string,'metadata':string}]}
def exec_search(query, category=None, page=0):
    #sqs = SearchQuerySet().raw_search(query)
    category='Classes'
    q = string.join([a+"*" for a in query.split()])
    q = q + ' django_ct:"main.class"'
    sqs = SearchQuerySet().raw_search(q)
    numpages = len(sqs)/RESULTS_PER_PAGE+1
    tmp = [a.object for a in sqs[page*RESULTS_PER_PAGE:(page+1)*RESULTS_PER_PAGE]]
    results = [{'title':a.title[0:43]+"..." if len(a.title)>46 else a.title, 'description':a.description[0:250]+'...' if len(a.description)>253 else a.description, 'metadata':'Class Numbers: '+string.join([x.number for x in a.classnumber_set.all()],', '), 'link':reverse("main.search_views.parties_by_class", kwargs={'pk':a.pk})} for a in tmp]
    return {'page':page,'numpages':numpages, 'results':results}

def search_page(request):
    rc={}
    query = request.GET.get('q','')
    category = request.GET.get('c',None)
    page = request.GET.get('page',0)
    rc['query']=query
    rc['category']=category
    tmp = exec_search(query=query, category=category, page=page)
    rc['results']=tmp['results']
    rc['numpages']=tmp['numpages']
    rc['page']=tmp['page']
    return render_to_response("main/search/search_page.html", rc, context_instance=RequestContext(request))

def ajax_s(request):
    result={'status':"none"}
    try:
        if request.method=="GET":
            verb = request.GET.get('verb',None)
            query = request.GET.get('q',None)
            category = request.GET.get('c',None)
            page = request.GET.get('page',0)
            if verb=='search_page':
                tmp = exec_search(query=query, category=category, page=page)
                result['results']=tmp['results']
                result['numpages']=tmp['numpages']
                result['page']=tmp['page']
                result['status']="success"
            else:
                result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")
