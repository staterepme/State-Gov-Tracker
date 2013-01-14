# Add Photo URLs#

import os, sys, re, urllib2

from urllib2 import HTTPError

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0]) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *

"""Loops through legislators without any photourls, tries to add them"""

print Officials.objects.filter(active="True", photourl="").count()

for off in Officials.objects.filter(active="True", photourl=""):
    regex = re.compile(r'(\d+$)')
    result = regex.search(off.homepage)
    if result:
        if off.chamber == "upper":
            off.photourl = 'http://www.pasen.gov/members/districts/sd%s/images/%s.jpg' % (off.district, result.group(0))
        else:
            off.photourl = 'http://www.house.state.pa.us/members/districts/%s/images/%s.jpg' % (off.district, result.group(0))
        try:
            urllib2.urlopen(off.photourl)
            off.save()
        except HTTPError:
            pass