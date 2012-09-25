from django.conf.urls import patterns, include, url
from django.conf import settings

''' Uncomment these when you're ready to integrate stuff from Chris's project
from StateGovTracker_Django.views import home
from StateGovTracker_Django.views import MyRep
from StateGovTracker_Django.views import search_form
from StateGovTracker_Django.views import search
from StateGovTracker_Django.views import search_results


urlpatterns = patterns('',
	('^$', search_form),
    ('^MyRep$', MyRep),
    ('^search$', search_form),
    ('^searches$', search_results),
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
