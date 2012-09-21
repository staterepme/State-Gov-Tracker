from django.conf.urls.defaults import *
from StateGovTracker_Django.views import home
from StateGovTracker_Django.views import MyRep
from StateGovTracker_Django.views import search_form
from StateGovTracker_Django.views import search


urlpatterns = patterns('',
	('^$', home),
    ('^MyRep$', MyRep),
    ('^search$', search_form),
    ('^searches$', search),
)