from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *

#Uncomment these when you're ready to integrate stuff from Chris's project
#in chris's these were all from StateGovTracker_Django.views import *
#from state_gov_tracker_app.views import home
from state_gov_tracker_app.views import MyRep
from state_gov_tracker_app.views import search_form
from state_gov_tracker_app.views import search
#from state_gov_tracker_app.views import search_results
from state_gov_tracker_app.views import WhichRep
from state_gov_tracker_app.views import profile, pa_tweets, about_myrep
from blog.views import Blog, Article

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    ('^$', search_form),
    ('^results$', WhichRep),
    ('^MyRep$', MyRep),
    ('^profile/(.*)$', profile),
    ('^pa-tweets$', pa_tweets),
    ('^about$', about_myrep),
    url(r'blog$', Blog),
    url(r'blog/post_num/(.*)$', Article),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

'''

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^current_time/', 'state_gov_tracker_app.views.current_datetime'),
    url(r'^twitter_test/', 'state_gov_tracker_app.views.twitter_view'),
    url(r'^$', 'state_gov_tracker_app.views.home', name='home'),
    # url(r'^state_gov_tracker/', include('state_gov_tracker.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
'''