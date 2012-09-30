#!/usr/bin/python

# Filename:	find_leg_homepages.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Uses openstates API to find legislator homepages

import sunlight
import pprint
from load_database import *

pp = pprint.PrettyPrinter(indent=4)

def get_leg_ids():
	legids = []
	query = session.query(official_info).all()
	for leg in query:
		legids.append(leg.legid)
	return legids

def get_urls_from_openstates(legids_list):
	url_legid_dict = {}
	for legid in legids_list:
		try:
			leg = sunlight.openstates.legislator_detail(legid)
			url_legid_dict[legid] = leg['url']
		except:
			print "No URL or LEGID for %s" %(legid)
	return url_legid_dict

def add_urls_to_db(url_legid_dict):
	"""Takes list of dictionaries that are of the form
	legid:url and adds it to database."""
	query = session.query(official_info).filter(official_info.homepage==None).all()
	for leg in query:
		try:
			leg.homepage = url_legid_dict[leg.legid]
			session.add(leg)
			session.commit()
		except:
			"No URL or KEYID for %s" %(leg.legid)

if __name__ == '__main__':
	legid_list = get_leg_ids()
	list_dict = get_urls_from_openstates(legid_list)
	# print list_dict
	add_urls_to_db(list_dict)