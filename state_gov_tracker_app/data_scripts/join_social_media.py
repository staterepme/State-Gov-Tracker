# join_social_media.py #

import os, sys

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0]) 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *

def update_social_media():
    """Function that updates social media data from original table"""
    for counter, official in enumerate(Officials.objects.all()):
        if counter % 5 == 0:
            print counter
        if official.facebook == "":
            official.facebook = LegsSocialmedia.objects.get(pk=official.legid).facebook
        if official.twitter == "":
            official.twitter = LegsSocialmedia.objects.get(pk=official.legid).twitter
        official.save()
