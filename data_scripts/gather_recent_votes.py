#!/usr/bin/python

# Filename:	find_leg_homepages.py
# Author: 	Christopher M. Brown
# Project: 	State Gov Track
# Task:		Uses openstates API to find legislator homepages

import sunlight
import pprint
from load_database import *

pp = pprint.PrettyPrinter(indent=4)

def get_downloaded_bills():
	bill_ids = []
	for bill in session.query(pa_bills).all():
		bill_ids.append(bill.bill_id)
	return bill_ids

def get_recent_bills():
	"""Returns a List of Recent Bills."""
	bills = sunlight.openstates.bills(state="PA", search_window="term")
	return bills

def get_bill_detail(bill_id_to_lookup):
	return sunlight.openstates.bill_detail(bill_id=bill_id_to_lookup, state="pa", session="2011-2012")

def add_bills_to_db():
	dl_bills = get_downloaded_bills()
	bills = get_recent_bills()
	print "Total of %s bills to gather" %(len(bills))
	counter = 0
	for bill in bills:
		if bill['bill_id'] in dl_bills:
			continue
		new_bill = pa_bills(state="pa", session=bill['session'], title=bill['title'], type=bill['type'][0], chamber=bill['chamber'], created_at=bill['created_at'], updated_at=bill['updated_at'], bill_id=bill['bill_id'])
		session.add(new_bill)
	session.commit()

if __name__ == '__main__':
	# get_downloaded_bills()
	add_bills_to_db()