# Update Officials in Database #

# Filename: download_officials.py
# Author:   Christopher M. Brown
# Project:  State Gov Track
# Task:     Uses openstates API to find legislators and add to database

import os
import sys

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from sunlight import openstates
import pprint
from state_gov_tracker_app.models import *

pp = pprint.PrettyPrinter(indent=4)


# Download Current Legislators #
def download_current_legislators():
    pa_legislators = openstates.legislators(
                        state='pa',
                        active='true')
    for counter, leg in enumerate(pa_legislators):
        if counter % 5 == 0:
            print counter
        if Officials.objects.filter(pk=leg['id']).exists():
            off = Officials.objects.get(pk=leg['id'])
            off.chamber = leg['chamber']
            off.createdat = leg['created_at']
            off.updatedat = leg['updated_at']
            if 'photo_url' in leg:
                off.photourl = leg['photo_url']
            off.district = leg['district']
            off.party = leg['party']
            if 'transparencydata_id' in leg:
                off.transparencydataid = leg['transparencydata_id']
            off.save()
        else:
            new_off = Officials(legid=leg['leg_id'],
                fullname=leg['full_name'],
                firstname=leg['first_name'],
                middlename=leg['middle_name'],
                lastname=leg['last_name'],
                suffixes=leg['suffixes'],
                active=leg['active'],
                state=leg['state'],
                chamber=leg['chamber'],
                district=leg['district'],
                party=leg['party'],
                createdat=leg['created_at'],
                updatedat=leg['updated_at'],
                homepage=leg['url'])
            if 'transparencydata_id' in leg:
                new_off.transparencydataid = leg['transparencydata_id']
            if 'photo_url' in leg:
                new_off.photourl = leg['photo_url']
            new_off.save()


# Check to see if legislators are active #

def update_active_status():
    legislators_in_db = Officials.objects.all()
    print len(legislators_in_db)
    for counter, leg in enumerate(legislators_in_db):
        if counter % 5 == 0:
            print "Updated Active status of %s Legislators so far" % (counter)
        openstates_detail = openstates.legislator_detail(leg.legid)
        leg.active = openstates_detail['active']
        leg.save()

if __name__ == '__main__':
    download_current_legislators()
    update_active_status()
