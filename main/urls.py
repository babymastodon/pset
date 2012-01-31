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
    url(r'^profile/(?P<pk>\d+)/$', 'profile_page'),#page for displaying profile info such as comments, personal info, classes
    url(r'^profile/me/$', 'my_profile_page'),#basically a wrapper for the previous rule but using the pk of the logged-in user
    url(r'^profile/bio/$', 'bio_info'),#page for editing profile info
    url(r'^profile/settings/$', 'account_info'),#page for editing profile info
    url(r'^newaccount/bio/$', 'new_bio_info'),#page for editing profile info
    url(r'^newaccount/$', 'create_account_page'),#gives a form to create an accoutn from email, or possibly ssl certificate
    url(r'^newaccount/email_sent$', 'email_sent'),#the verification email has been sent
    url(r'^account/reset_email_sent$', 'reset_email_sent'),#the verification email has been sent
    url(r'^newaccount/verify/(?P<hashcode>.+)/$', 'verify'),#the user gets sent an email and the verification link goes here, the verification link will have a unique hash
    url(r'^account/reset/(?P<hashcode>.+)/$', 'reset_password_hashcode'),#the user gets sent an email and the verification link goes here, the verification link will have a unique hash
    url(r'^account/chpass/$', 'change_password'),#the user gets sent an email and the verification link goes here, the verification link will have a unique hash
    url(r'^newaccount/info/$', 'verify'),#the page where a new user inputs info such as major, grade, etc, connect with facebook, etc.
    url(r'^linkaccount/facebook/$', 'link_to_facebook'),#page when the user wants to link account to facebook
    url(r'^login/$', 'login_page'),#the view that processes the login form, redirecting to profile/me/ if successful, redisplaying the form if not
    url(r'^logout/$', 'logout_view'),#logs the user out and redirects to front page
    url(r'^logout/main/$', lambda x: HttpResponseRedirect('/')),
    url(r'^forgotpw/$', 'forgot_password'),
    url(r'^facebook/', include('django_facebook.urls')),
    url(r'^manage_classes/', 'manage_classes'),
    url(r'^newaccount/invite/(?P<hashcode>.+)/(?P<pk>\d+)/$', 'invite_hashcode'),
)

#search views
urlpatterns += patterns('main.search_views',
    url(r'^parties/class/(?P<pk>\d+)/$', 'parties_by_class'),#list the upcoming parties for this class
    url(r'^parties/date/$', 'parties_by_date'),#list parties by day for the next week
    url(r'^search/$', 'search_page'),#search page for classes and people
)

#class views
urlpatterns += patterns('main.class_views',
    url(r'^class/(?P<pk>\d+)/$', 'class_details'),#class page- list of students, party schedule, "subscribe button", resources
    url(r'^class/upload/$', 'class_file_upload'),#iframe for receiving file uploads
)

#party views
urlpatterns += patterns('main.party_views',
    url(r'^party/(?P<pk>\d+)/$', 'party_details'),#detailed lsit of party details, party admins can update vales via ajax
    url(r'^party/registered/(?P<pk>\d+)/$', 'party_registered'),#view after a successful party registration
    url(r'^party/unregistered/(?P<pk>\d+)/$', 'party_unregistered'),#view after a successful party unregistration
    url(r'^party/login/(?P<pk>\d+)/$', 'party_must_login'),#view after a successful party unregistration
    url(r'^party/create/$', 'party_create'),#form for creating a new party
    url(r'^party/invite/(?P<pk>\d+)/$', 'invite_friends'),#form for creating a new party
    url(r'^party/edit/(?P<pk>\d+)/$', 'edit_party'),#form for creating a new party
    url(r'^party/cancel/(?P<pk>\d+)/$', 'party_cancel'),#form for creating a new party
    url(r'^party/uncancel/(?P<pk>\d+)/$', 'party_uncancel'),#form for creating a new party
    url(r'^calendar/(?P<historytype>\w+)/(?P<pk>\d+)/(?P<page>\d+)/(?P<time>\w+)/$', 'all_history'),
)

#views for the people ajax popup
urlpatterns += patterns('main.people_views',
    url(r'^party/attending/(?P<pk>\d+)/$', 'all_attending'),#view after a successful party unregistration
    url(r'^profile/followers/(?P<pk>\d+)/$', 'all_followers'),#view after a successful party unregistration
    url(r'^profile/followees/(?P<pk>\d+)/$', 'all_followees'),#view after a successful party unregistration
    url(r'class/members/(?P<pk>\d+)/$', 'all_members'),#view after a successful party unregistration
)

#the ajax handler
urlpatterns += patterns('main.ajax_views',
        url(r'^ajax', 'ajax'),
)

#misc views
urlpatterns += patterns('main.common_views',
    url(r'^newsfeed/(?P<feedtype>\w+)/(?P<pk>\d+)/(?P<page>\d+)/$', 'all_newsfeed'),
    url(r'^calendar/(?P<feedtype>\w+)/(?P<pk>\d+)/(?P<page>\d+)/$', 'all_newsfeed'),
    url(r'^socialbuttons/$', 'social_buttons'),
)
