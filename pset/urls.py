from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pset.views.home', name='home'),
    # url(r'^pset/', include('pset.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url('^'+getattr(settings,"LOGIN_URL","/accounts/login/")[1:]+'$', 'django.contrib.auth.views.login', name='login'),
    url('^'+getattr(settings,"LOGOUT_URL","/accounts/login/")[1:]+'$', 'django.contrib.auth.views.logout', name='logout'),
    url('^', include('main.urls')),
)
