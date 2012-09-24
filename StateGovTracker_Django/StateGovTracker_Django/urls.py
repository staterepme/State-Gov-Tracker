from django.conf.urls.defaults import *
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