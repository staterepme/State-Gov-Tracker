#!/usr/bin/python

# Filename: gather_addresses.py
# Author:   Christopher M. Brown
# Project:  State Gov Track
# Task:     Uses openstates API to find legislator office information (location, phone number, etc.)

from sunlight import openstates
import pprint

import sys, os

# Need to add django application to path #
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
split_path = os.path.split(parentdir)
sys.path.insert(0, split_path[0])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

from state_gov_tracker_app.models import *
from state_gov_tracker_app.login_credentials import *

pp = pprint.PrettyPrinter(indent=4)


def add_addresses_to_db():
    OfficialOffices.objects.all().delete()
    counter = 0
    for off in Officials.objects.all():
        counter += 1
        if counter % 20 == 0:
            print "Finished gathering addresses for %s Legislators" % (counter)
        try:
            leg_info = openstates.legislator_detail(off.legid)
        except:
            print "Could not get OpenStates information for legid:%s\nname:%s" % (off.legid, off.fullname)
            continue
        for office in leg_info['offices']:
            new_office = OfficialOffices(office_legid=off.legid,
                address=office['address'],
                phone=office['phone'],
                name=office['name'])
            new_office.save()

if __name__ == '__main__':
    add_addresses_to_db()
    # pp.pprint(openstates.legislator_detail('PAL000001'))
