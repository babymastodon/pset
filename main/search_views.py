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
from haystack.query import SearchQuerySet
from haystack.inputs import Raw
import logging, simplejson, string, re, urllib, random
from django.core import serializers

#import models and forms here
from main.models import *
from main.forms import *
from main.views_common import *

RESULTS_PER_PAGE = getattr(settings,'RESULTS_PER_PAGE',10)
logger = logging.getLogger(__name__)

def parties_by_class(request, pk):
    rc={}
    rc['pk']=pk
    c = get_object_or_404(Class, pk=pk)
    rc['class_name'] = c.title
    return render_to_response("main/search/parties_by_class.html", rc, context_instance=RequestContext(request))

def userinfo_by_username(request, pk):
    rc = {}

def parties_by_date(request):
    rc={}
    day_list=[]
    today = date.today()
    day_list.append('Today')
    day_list.append('Tomorrow')
    for i in range(2,6):
        delta = timedelta(days=i)
        day_list.append((today+delta).strftime("%A").capitalize())
    rc['day_list']=day_list
    rc['selected_day']=int(request.GET.get('day','0'))
    return render_to_response("main/search/parties_by_date.html", rc, context_instance=RequestContext(request))

trunc = lambda s,n: s if len(s)<n-3 else s[:n-3]+"..."

#takes a search query and an optional category. If no category, it tries to intelligently guess the
#cagetory. If the search query contains a class number, the search will try to make that result first
#it returns a dict with name, description, (picture), and related classes if a class. If a person,
#returns dict with name, class, department, (picture)
#format: {'page':int, 'numpages':int, 'results':[{'title':string,'description':string,'metadata':string}]}
def exec_search(query, category=None, page=1, force_category=False):
    numpages=1
    result_items=[]
    pageresults=0
    totalresults=0
    sqs=None
    if query:
        """
            Slight change to algorithm: check if there are any matches in current category. If
            there are none, but matches are present in another category, switch to that one 
            instead. 
        """
        wildcard_tokens = string.join([a + "* OR " + a for a in query.split()], " OR ")
        user_search = SearchQuerySet().filter(content = Raw(wildcard_tokens)).models(UserInfo)
        class_search = SearchQuerySet().filter(content=Raw(wildcard_tokens)).models(Class)
        if not category:
            category = "Classes"
        if (not force_category) and ((category == "People" and len(user_search) == 0) or (category == "Classes" and len(class_search) == 0)):
            # if no results in category, attempt to switch categories. search by class is preferred
            if len(class_search) < len(user_search):
                category="People"
            elif len(class_search) > len(user_search):
                category="Classes"
        if category=="Classes":
            if re.match(".*\d|\..*", query) or (len(query)==2 and query.lower() in ['cc','ec','es','as','ms','ns','cm','cs','hs','ma','st','sw']) or (len(query)==3 and query.lower() in ['cms','csb','esd','hst','mas','sts','swe']): 
                #if they are searching for a class number, matches prefixes for course numbers that start in letters
                sqs = SearchQuerySet().raw_search(wildcard_tokens).models(ClassNumber)
            else:
                sqs=class_search
            totalresults = len(sqs)
            numpages = totalresults/RESULTS_PER_PAGE+1
            tmp = [a.object for a in sqs[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE]]
            for a in tmp:
                item={}
                item['title'] = trunc(a.get_title(),45)
                item['description'] = trunc(a.get_description(),250)
                item['metadata'] = 'Class Numbers: '+string.join([x.number for x in a.get_meta()],', ')
                item['link']=reverse("main.search_views.parties_by_class", kwargs={'pk':a.pk})
                result_items.append(item)
            pageresults=len(result_items)
        if category=="People":
            sqs = user_search
            totalresults = len(sqs)
            numpages = totalresults/RESULTS_PER_PAGE+1
            tmp = [a.object for a in sqs[(page-1)*RESULTS_PER_PAGE:page*RESULTS_PER_PAGE]]
            for a in tmp:
                item = {}
                item['title'] = trunc(a.get_title(), 30)
                item['description'] = trunc(a.get_description(), 250)
                item['metadata'] = a.get_meta()
                item['link'] = reverse("main.search_views.parties_by_class", kwargs={'pk':a.pk})
                result_items.append(item)
            pageresults=len(result_items)
    prwidth = 3
    bottom = max(1, page-prwidth)
    top = min(numpages+1, bottom + 1 + 2* prwidth)
    bottom = max(1, top - 2 * prwidth - 1)
    pagerange = range(bottom, top)
    rmin = RESULTS_PER_PAGE*(page-1)+1
    rmax = rmin+pageresults-1
    if totalresults==0:
        rmin=rmax=0
    return {'page':page,'numpages':numpages, 'result_items':result_items, 'category':category, 'pageresults':pageresults, 'totalresults':totalresults, 'pagerange':pagerange, 'rmin':rmin, 'rmax':rmax, 'status':'success'}

def autocomplete_classes(query):
    wildcard_tokens = string.join([a + "* OR " + a for a in query.split()], " OR ")
    sqs = SearchQuerySet().raw_search(wildcard_tokens).models(ClassNumber)
    def shorten(s):
        if len(s)>33:
            return s[:30]+"..."
        return s
    nums = [shorten(a.text) for a in sqs[0:5]]
    if nums:
        return {"status":"success", 'result': nums}
    else:
        return {'status': "no results found"}

def create_party_dict(pk, letter, request, color="red", day="0"):
    (lat,lng) = [(random.random()-.5)*.01+x for x in (42.35886, -71.09356)]
    r = {}
    r['title'] = "Blah BLah PARTY TIME blah moo?"
    r['letter'] = letter
    r['day'] = "0"
    r['day_name'] = "Toosday"
    r['date_number'] = "1/1/1"
    r['start_time'] = "9:00"
    r['end_time'] = "9:00"
    r['agenda'] = "Description"
    r['location'] = "Location"
    r['bldg_num'] = "W11"
    r['detail_url'] = "detail link"
    r['bldg_img'] = 'http://web.mit.edu/campus-map/objimgs/object-W35.thumb.jpg'
    r['lat'] = lat
    r['lng'] = lng
    r['class_nums'] = ['5.111','5.112']
    r['class_title'] = "Principles of Chemistry"
    r['color'] = color
    r['pk'] = 0
    r['friends_attending'] = 3
    r['friends'] = 10
    return r

def get_parties_by_class(request, class_pk):
    result_list=[]
    #available colors are: blue brown darkgreen green orange paleblue pink purple red yellow
    colorlist = ['red','orange','yellow','green','blue','purple']
    for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        r = create_party_dict("0", i, request)
        result_list.append(r)
    return {'status':'success', 'result_list':result_list}

def get_parties_by_date(request, day):
    result_list=[]
    #available colors are: blue brown darkgreen green orange paleblue pink purple red yellow
    colorlist = ['red','orange','yellow','green','blue','purple']
    todays_color = colorlist[int(day)]
    for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        r = create_party_dict("0", i, request, day=day, color=todays_color)
        result_list.append(r)
    return {'status':'success', 'result_list':result_list}

def search_page(request):
    rc={}
    query = request.GET.get('q','')
    category = request.GET.get('c',None)
    page = int(request.GET.get('page',"1"))
    rc['query']=query
    rc['results'] = exec_search(query=query, category=category, page=page)
    if (page!=rc['results']['numpages']):
        rc['url_next_page']=request.path+"?"+urllib.urlencode({'q':query, 'c':rc['results']['category'], 'page':page+1})
    if (page!=1):
        rc['url_prev_page']=request.path+"?"+urllib.urlencode({'q':query, 'c':rc['results']['category'], 'page':page-1})
    rc['url_no_page']=request.path+"?"+urllib.urlencode({'q':query, 'c':category})+"&page="
    return render_to_response("main/search/search_page.html", rc, context_instance=RequestContext(request))

def ajax(request):
    result={'status':"none"}
    try:
        if request.method=="GET":
            verb = request.GET.get('verb',None)
            if verb=='search_page':
                query = request.GET['q']
                category = request.GET.get('c',None)
                page = int(request.GET.get('page',"0"))
                force_category = int(request.GET.get('force',"0"))!=0
                result = exec_search(query=query, category=category, page=page, force_category=force_category)
            elif verb=='parties_by_class':
                class_pk = request.GET['class']
                result = get_parties_by_class(request, class_pk)
            elif verb=='parties_by_date':
                day = request.GET['day']
                result = get_parties_by_date(request, day)
            elif verb=='class_suggestions':
                query = request.GET['q']
                result = exec_search(query=query, category="Classes", page=1, force_category=True)
            elif verb=="autocomplete_class":
                query = request.GET['q']
                result = autocomplete_classes(query) 
            else:
                result['status']="verb didn't match"
    except Exception as e:
        result['status']="error: "+ str(e)
    json=simplejson.dumps(result)
    return HttpResponse(json, mimetype="application/json")
