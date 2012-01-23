from django.conf.urls import patterns, include, url
from django.http import HttpResponseRedirect

#generic views
urlpatterns = patterns('main.home_views',
    url(r'^$', 'front_page'),#the first page
    url(r'^home/$', 'home_page'),#the personalized home page with Notifications etc
    url(r'^about/$', 'about'),#about page
)   

#account-related views
urlpatterns += patterns('main.account_views',
    url(r'^profile/(?P<pk>d+)/$', 'profile_page'),#page for displaying profile info such as comments, personal info, classes
    url(r'^profile/me/$', 'my_profile_page'),#basically a wrapper for the previous rule but using the pk of the logged-in user
    url(r'^profile/edit/$', 'profile_edit'),#page for editing profile info
    url(r'^newaccount/$', 'create_account_page'),#gives a form to create an accoutn from email, or possibly ssl certificate
    url(r'^newaccount/verify/(?P<hashcode>.+)/$', 'verify'),#the user gets sent an email and the verification link goes here, the verification link will have a unique hash
    url(r'^newaccount/info/$', 'verify'),#the page where a new user inputs info such as major, grade, etc, connect with facebook, etc.
    url(r'^linkaccount/facebook/$', 'link_to_facebook'),#page when the user wants to link account to facebook
    url(r'^login/$', 'login_page'),#the view that processes the login form, redirecting to profile/me/ if successful, redisplaying the form if not
    url(r'^logout/$', 'logout_view'),#logs the user out and redirects to front page
    url(r'^logout/main/$', lambda x: HttpResponseRedirect('/')),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^accounts/', include('userena.urls')),
)

#search views
urlpatterns += patterns('main.search_views',
    url(r'^parties/class/(?P<pk>\d+)/$', 'parties_by_class'),#list the upcoming parties for this class
    url(r'^parties/date/$', 'parties_by_date'),#list parties by day for the next week
    url(r'^search/$', 'search_page'),#search page for classes and people
)

#class views
urlpatterns += patterns('main.class_views',
    url(r'^class/(?P<pk>)/$', 'class_details'),#class page- list of students, party schedule, "subscribe button", resources
    url(r'^class/upload/$', 'class_file_upload'),#iframe for receiving file uploads
)

#party views
urlpatterns += patterns('main.party_views',
    url(r'^party/(?P<pk>\d+)/$', 'party_details'),#detailed lsit of party details, party admins can update vales via ajax
    url(r'^party/registered/(?P<pk>\d+)/$', 'party_registered'),#view after a successful party registration
    url(r'^party/create/$', 'party_create'),#form for creating a new party
)

#the ajax handler
urlpatterns += patterns('main.ajax_views',
        url(r'ajax', 'ajax'),
)
