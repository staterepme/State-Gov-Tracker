#!/usr/bin/python

# Filename:	gather_addresses.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Uses openstates API to find legislator office information (location, phone number, etc.)

from sunlight import openstates
import pprint
from load_database import *

pp = pprint.PrettyPrinter(indent=4)

def get_leg_ids():
	legids = []
	query = session.query(official_info).all()
	for leg in query:
		legids.append(leg.legid)
	return legids

def add_addresses_to_db():
	legids = get_leg_ids()
	print "Need to download addresses for %s Legislators" %(len(legids))
	counter = 0
	for legid_to_get in legids:
		counter += 1
		if counter % 20 == 0:
			print "Finished gathering addresses for %s Legislators" %(counter)
		try:
			leg_info = openstates.legislator_detail(legid_to_get)
		except:
			print "Could not get OpenStates information for legid:%s" %(legid_to_get)
			continue
		for office in leg_info['offices']:
			new_office = offices(office_legid=legid_to_get, address=office['address'], phone=office['phone'], name=office['name'])
			session.add(new_office)
		session.commit()

if __name__ == '__main__':
	# add_addresses_to_db()
	pp.pprint(openstates.legislator_detail('PAL000001'))